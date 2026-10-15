"""Quais defesas de memória um binário já carrega.

Em C a linguagem não impede um programa de escrever fora de um buffer; o
processador e o compilador ajudam com defesas que tornam a exploração
cara: NX (dados não executam), PIE+ASLR (endereços mudam a cada execução),
RELRO (a tabela de ligação vira somente-leitura) e o canário de pilha (um
valor que, se sobrescrito, aborta o programa com "stack smashing detected"
em vez de desviar o fluxo).

Esta ferramenta LÊ um binário e diz quais dessas defesas ele tem. É o que
o `checksec` faz, feito com `readelf`/`objdump`, sem instalar nada. Puro
diagnóstico: não escreve, não explora, não altera o binário.

    python3 protecoes.py /caminho/para/o/binario
    python3 protecoes.py $(command -v ls)      # um binário do próprio sistema
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _roda(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def protecoes(binario: Path) -> dict[str, bool | str]:
    """Lê os cabeçalhos ELF e os símbolos. Campos booleanos; 'ferramenta' diz o que faltou."""
    if shutil.which("readelf") is None:
        return {"ferramenta": "readelf ausente (pacote binutils); sem diagnóstico"}
    cabecalhos = _roda(["readelf", "-lW", str(binario)])
    dinamico = _roda(["readelf", "-dW", str(binario)])
    simbolos = _roda(["readelf", "-sW", str(binario)])
    tipo = _roda(["readelf", "-hW", str(binario)])
    relro_parcial = "GNU_RELRO" in cabecalhos
    bind_now = "BIND_NOW" in dinamico or ("FLAGS_1" in dinamico and "NOW" in dinamico)
    return {
        # Pilha não-executável: o segmento GNU_STACK não pode ter permissão de execução (E).
        "nx": "GNU_STACK" in cabecalhos and not any(
            "GNU_STACK" in l and "RWE" in l for l in cabecalhos.splitlines()),
        # PIE: executável do tipo DYN carrega em endereço aleatório (com ASLR ligado no SO).
        "pie": "Type:" in tipo and "DYN (" in tipo,
        # Canário de pilha: o binário referencia a checagem do glibc.
        "canario": "__stack_chk_fail" in simbolos,
        # RELRO: parcial = GNU_RELRO presente; completo = também BIND_NOW.
        "relro": "completo" if (relro_parcial and bind_now) else "parcial" if relro_parcial else "ausente",
        # Fortify: versões _chk de funções de string (verificação de tamanho em tempo de compilação).
        "fortify": "_chk@" in simbolos or "_chk " in simbolos,
    }


def resumo(p: dict) -> str:
    if "ferramenta" in p:
        return p["ferramenta"]
    marca = lambda b: "sim" if b else "NÃO"
    return (f"NX {marca(p['nx'])} | PIE/ASLR {marca(p['pie'])} | canário {marca(p['canario'])} | "
            f"RELRO {p['relro']} | FORTIFY {marca(p['fortify'])}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    alvo = Path(sys.argv[1])
    if not alvo.is_file():
        print(f"não encontrei: {alvo}")
        raise SystemExit(2)
    print(f"{alvo}:")
    print(" ", resumo(protecoes(alvo)))
