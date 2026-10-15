"""O avaliador: mede a máquina e dá uma nota, com o motivo de cada desconto.

Mede, não supõe. Cada item que o SO não deixa verificar vira "não medido"
e conta como ausente (princípio 10: falhe fechado). Roda em Linux, sem root
para a maioria dos itens; alguns pedem root e dizem isso.

    python3 avaliar.py            # a nota de agora
    python3 avaliar.py --salvar   # grava a foto em fotos/<data>.json para comparar depois
    python3 avaliar.py --json     # saída em JSON, para script

A nota é só um resumo. O que vale é a lista de motivos: cada um é um item
do CHECKLIST.md com o comando que o prova.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

PASTA_FOTOS = Path(__file__).with_name("fotos")


@dataclass
class Item:
    nome: str
    peso: int
    ok: bool | None          # None = não foi possível medir
    detalhe: str

    @property
    def pontos(self) -> int:
        return self.peso if self.ok else 0


def _existe(p: str) -> bool:
    return Path(p).exists()


def _cmd(cmd: list[str]) -> tuple[int, str]:
    if shutil.which(cmd[0]) is None:
        return 127, ""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return r.returncode, r.stdout + r.stderr
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def medir() -> list[Item]:
    itens: list[Item] = []

    # Secure Boot (impede o não-assinado)
    efi = _existe("/sys/firmware/efi")
    if not efi:
        itens.append(Item("Secure Boot", 20, None, "máquina não iniciou em modo UEFI (ou sem acesso a /sys/firmware/efi)"))
    else:
        rc, saida = _cmd(["mokutil", "--sb-state"])
        if rc == 127:
            itens.append(Item("Secure Boot", 20, None, "mokutil ausente; instale para medir (pacote mokutil)"))
        else:
            ligado = "enabled" in saida.lower()
            itens.append(Item("Secure Boot", 20, ligado, "ligado" if ligado else "desligado: firmware aceita bootloader não assinado"))

    # TPM presente
    tpm = _existe("/dev/tpm0") or _existe("/dev/tpmrm0")
    itens.append(Item("TPM 2.0", 15, tpm, "presente em /dev/tpm*" if tpm else "ausente: sem raiz de confiança para medir o boot nem selar chaves"))

    # Disco cifrado
    rc, saida = _cmd(["lsblk", "-o", "TYPE,FSTYPE"])
    if rc == 127:
        itens.append(Item("Disco cifrado", 20, None, "lsblk ausente; sem como medir"))
    else:
        cifrado = "crypt" in saida or "crypto_LUKS" in saida
        itens.append(Item("Disco cifrado", 20, cifrado, "LUKS presente" if cifrado else "nenhum volume cifrado: disco fora do gabinete é legível"))

    # IOMMU (contra DMA)
    cmdline = Path("/proc/cmdline").read_text() if _existe("/proc/cmdline") else ""
    grupos = Path("/sys/kernel/iommu_groups")
    iommu = ("intel_iommu=on" in cmdline or "amd_iommu=on" in cmdline or
             (grupos.is_dir() and any(grupos.iterdir())))
    itens.append(Item("IOMMU", 15, iommu, "ativa: um dispositivo PCIe/Thunderbolt não lê a RAM inteira"
                      if iommu else "inativa: DMA de um periférico pode ler a memória"))

    # ASLR
    aslr_p = Path("/proc/sys/kernel/randomize_va_space")
    if aslr_p.exists():
        v = aslr_p.read_text().strip()
        itens.append(Item("ASLR", 10, v == "2", f"randomize_va_space={v}" + ("" if v == "2" else " (deveria ser 2)")))
    else:
        itens.append(Item("ASLR", 10, None, "não exposto por este kernel"))

    # Kernel lockdown (quando há Secure Boot)
    lock = Path("/sys/kernel/security/lockdown")
    if lock.exists():
        conteudo = lock.read_text()
        ligado = "[none]" not in conteudo
        itens.append(Item("Kernel lockdown", 10, ligado, conteudo.strip() if ligado else "none: módulos e /dev/mem sem restrição"))
    else:
        itens.append(Item("Kernel lockdown", 10, None, "lockdown não disponível neste kernel"))

    # Atualizações de firmware conhecidas
    rc, saida = _cmd(["fwupdmgr", "get-updates"])
    if rc == 127:
        itens.append(Item("Firmware (fwupd)", 10, None, "fwupd ausente; não dá para saber de atualizações de firmware"))
    else:
        sem_pendencia = "No updates" in saida or "Nenhuma atualiz" in saida or rc == 2
        itens.append(Item("Firmware (fwupd)", 10, sem_pendencia,
                          "sem atualização pendente" if sem_pendencia else "há atualização de firmware pendente"))

    return itens


def nota(itens: list[Item]) -> int:
    total = sum(i.peso for i in itens)
    obtido = sum(i.pontos for i in itens)
    return round(100 * obtido / total) if total else 0


def foto(itens: list[Item]) -> dict:
    return {
        "quando": dt.datetime.now().isoformat(timespec="seconds"),
        "maquina": platform.node(),
        "sistema": platform.platform(),
        "nota": nota(itens),
        "itens": [{"nome": i.nome, "peso": i.peso, "ok": i.ok, "detalhe": i.detalhe} for i in itens],
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    itens = medir()
    f = foto(itens)
    if args.json:
        print(json.dumps(f, indent=1, ensure_ascii=False))
    else:
        print(f"nota: {f['nota']}/100 ({f['maquina']}, {f['sistema']})\n")
        for i in itens:
            marca = {True: "ok ", False: "FALTA", None: "?  "}[i.ok]
            print(f"  [{marca}] {i.nome:18s} {i.detalhe}")
        print("\n  '?' = não foi possível medir; conta como ausente (falhe fechado).")
    if args.salvar:
        PASTA_FOTOS.mkdir(exist_ok=True)
        destino = PASTA_FOTOS / f"{dt.date.today().isoformat()}.json"
        destino.write_text(json.dumps(f, indent=1, ensure_ascii=False) + "\n")
        print(f"\n  foto salva em {destino.relative_to(Path(__file__).parent.parent)}")
