"""Inventário de USB e detecção de BadUSB (teclado que aparece sozinho).

Lê o sysfs do Linux (`/sys/bus/usb/devices`), sem precisar de root nem de
`lsusb`. Guarda a foto dos dispositivos; na próxima leitura, diz o que
entrou, o que saiu e, sobretudo, se entrou um dispositivo de interface
humana (HID, classe 03) que não estava na foto anterior: um "pen drive"
que se apresenta como teclado é exatamente isso.

    python3 usb.py                 # lista o que está plugado agora
    python3 usb.py --salvar        # guarda a foto em inventario-usb.json
    python3 usb.py --comparar      # diff com a foto guardada e alerta de HID novo

A árvore do sysfs é um parâmetro (`raiz`), para o teste usar uma árvore
falsa em vez de depender do hardware de quem roda.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

CLASSE_HID = "03"
ARQUIVO_FOTO = Path(__file__).with_name("inventario-usb.json")


@dataclass(frozen=True)
class Dispositivo:
    caminho: str
    fabricante_id: str
    produto_id: str
    nome: str
    serial: str
    classes: tuple[str, ...]  # classes das interfaces (03 = HID, 08 = armazenamento, ...)

    @property
    def e_hid(self) -> bool:
        return CLASSE_HID in self.classes

    @property
    def chave(self) -> str:
        return f"{self.fabricante_id}:{self.produto_id}:{self.serial or self.caminho}"


def _ler(p: Path) -> str:
    try:
        return p.read_text(errors="replace").strip()
    except OSError:
        return ""


def listar(raiz: Path = Path("/sys/bus/usb/devices")) -> list[Dispositivo]:
    """Dispositivos (não interfaces) sob a raiz. Interface = nome com ':' (ex.: 1-2:1.0)."""
    saida = []
    if not raiz.is_dir():
        return saida
    for d in sorted(raiz.iterdir()):
        if ":" in d.name or not (d / "idVendor").exists():
            continue
        classes = tuple(sorted({_ler(i / "bInterfaceClass") for i in raiz.iterdir()
                                if i.name.startswith(d.name + ":") and (i / "bInterfaceClass").exists()}))
        saida.append(Dispositivo(
            caminho=d.name, fabricante_id=_ler(d / "idVendor"), produto_id=_ler(d / "idProduct"),
            nome=(_ler(d / "manufacturer") + " " + _ler(d / "product")).strip(),
            serial=_ler(d / "serial"), classes=classes))
    return saida


def comparar(antes: list[Dispositivo], agora: list[Dispositivo]) -> dict:
    chaves_antes = {d.chave for d in antes}
    chaves_agora = {d.chave for d in agora}
    novos = [d for d in agora if d.chave not in chaves_antes]
    sumiram = [d for d in antes if d.chave not in chaves_agora]
    return {
        "novos": novos,
        "sumiram": sumiram,
        # O alerta: HID que não estava na foto. Teclado novo numa máquina que
        # já tinha o seu é, na melhor hipótese, alguém plugando algo; na pior, BadUSB.
        "hid_novo": [d for d in novos if d.e_hid],
    }


def salvar(dispositivos: list[Dispositivo], arquivo: Path = ARQUIVO_FOTO) -> None:
    arquivo.write_text(json.dumps([asdict(d) for d in dispositivos], indent=1, ensure_ascii=False) + "\n")


def carregar(arquivo: Path = ARQUIVO_FOTO) -> list[Dispositivo]:
    if not arquivo.exists():
        return []
    return [Dispositivo(**{**d, "classes": tuple(d["classes"])}) for d in json.loads(arquivo.read_text())]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    ap.add_argument("--comparar", action="store_true")
    args = ap.parse_args()
    agora = listar()
    for d in agora:
        print(f"{d.caminho:8s} {d.fabricante_id}:{d.produto_id}  {d.nome:40s} classes={','.join(d.classes) or '-'}{'  HID' if d.e_hid else ''}")
    if not agora:
        print("nenhum dispositivo USB visível (sem sysfs? container?)")
    if args.salvar:
        salvar(agora)
        print(f"foto salva em {ARQUIVO_FOTO.name}: {len(agora)} dispositivos")
    if args.comparar:
        r = comparar(carregar(), agora)
        print(f"novos: {len(r['novos'])}  sumiram: {len(r['sumiram'])}")
        for d in r["hid_novo"]:
            print(f"ALERTA: dispositivo de entrada novo: {d.nome or d.chave}. Se você não plugou um teclado agora, desplugue.")
        raise SystemExit(2 if r["hid_novo"] else 0)
