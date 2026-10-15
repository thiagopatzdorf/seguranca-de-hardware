"""Manifesto de integridade: um hash por arquivo, verificação que pega troca.

Serve para o `/boot` (kernel, initrd, bootloader), para a pasta de drivers,
para um dump de firmware lido com `flashrom`: qualquer conjunto de arquivos
que deveria mudar só quando você manda.

    python3 manifesto.py gerar /boot manifesto-boot.json
    python3 manifesto.py verificar /boot manifesto-boot.json

O manifesto é a "foto". Guarde-o fora da máquina: um manifesto no mesmo
disco que um atacante com root controla é um manifesto que ele reescreve.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def hash_arquivo(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def gerar(raiz: Path) -> dict[str, str]:
    """Caminho relativo -> sha256, só de arquivos regulares (links e dispositivos ficam de fora)."""
    manifesto = {}
    for p in sorted(raiz.rglob("*")):
        if p.is_file() and not p.is_symlink():
            try:
                manifesto[str(p.relative_to(raiz))] = hash_arquivo(p)
            except OSError:
                manifesto[str(p.relative_to(raiz))] = "ilegivel"
    return manifesto


def verificar(raiz: Path, esperado: dict[str, str]) -> dict[str, list[str]]:
    atual = gerar(raiz)
    return {
        "alterados": sorted(k for k in esperado if k in atual and atual[k] != esperado[k]),
        "sumiram": sorted(k for k in esperado if k not in atual),
        "novos": sorted(k for k in atual if k not in esperado),
    }


def integro(resultado: dict[str, list[str]]) -> bool:
    return not any(resultado.values())


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("gerar", "verificar"):
        print(__doc__)
        raise SystemExit(2)
    acao, raiz, arquivo = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    if acao == "gerar":
        m = gerar(raiz)
        arquivo.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
        print(f"{len(m)} arquivos em {raiz} -> {arquivo}")
    else:
        r = verificar(raiz, json.loads(arquivo.read_text()))
        for tipo, lista in r.items():
            for k in lista:
                print(f"{tipo:9s} {k}")
        print("íntegro" if integro(r) else f"DIFERENTE: {sum(len(v) for v in r.values())} item(ns)")
        raise SystemExit(0 if integro(r) else 1)
