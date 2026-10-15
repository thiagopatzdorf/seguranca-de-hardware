"""Atestação como o TPM faz: PCRs, extend e quote.

Um PCR (Platform Configuration Register) não aceita escrita; aceita só
`extend`:  PCR = SHA256(PCR || medida). Isso dá três propriedades que o
boot medido precisa:

- não dá para "voltar" um PCR (não existe inverso do hash);
- a ordem importa (extend(a) depois extend(b) != extend(b) depois extend(a));
- qualquer componente diferente, em qualquer ponto, muda o valor final.

O *quote* é o TPM assinando o conjunto de PCRs com uma chave que nunca sai
do chip (aqui, uma chave Ed25519 que só o objeto TPM conhece). Quem
verifica compara com a política: "PCR 0 e 7 precisam valer isto".

Se existir um TPM de verdade e o `tpm2-tools` instalado, `ler_pcrs_reais()`
lê os PCRs da máquina; se não, diz que não há, sem fingir.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass, field

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

ZERO = bytes(32)


def extend(valor_atual: bytes, medida: bytes) -> bytes:
    return hashlib.sha256(valor_atual + hashlib.sha256(medida).digest()).digest()


@dataclass
class TPM:
    """Um TPM de brinquedo: 24 PCRs e uma chave de atestação que não sai daqui."""

    pcrs: dict[int, bytes] = field(default_factory=lambda: {i: ZERO for i in range(24)})
    _chave: Ed25519PrivateKey = field(default_factory=Ed25519PrivateKey.generate, repr=False)

    def extend(self, indice: int, medida: bytes) -> bytes:
        self.pcrs[indice] = extend(self.pcrs[indice], medida)
        return self.pcrs[indice]

    def chave_publica_pem(self) -> bytes:
        return self._chave.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)

    def quote(self, indices: list[int], nonce: bytes) -> dict:
        """Assina os PCRs pedidos + um nonce do verificador (contra replay)."""
        corpo = {"pcrs": {str(i): self.pcrs[i].hex() for i in indices}, "nonce": nonce.hex()}
        serializado = json.dumps(corpo, sort_keys=True).encode()
        return {"corpo": corpo, "assinatura": self._chave.sign(serializado).hex()}


def verificar_quote(quote: dict, chave_publica_pem: bytes, nonce: bytes, politica: dict[int, bytes]) -> list[str]:
    """Devolve a lista de problemas; vazia = atestação aceita."""
    problemas = []
    publica = serialization.load_pem_public_key(chave_publica_pem)
    assert isinstance(publica, Ed25519PublicKey)
    serializado = json.dumps(quote["corpo"], sort_keys=True).encode()
    try:
        publica.verify(bytes.fromhex(quote["assinatura"]), serializado)
    except InvalidSignature:
        return ["assinatura do quote inválida: não veio deste TPM ou foi alterado"]
    if quote["corpo"]["nonce"] != nonce.hex():
        problemas.append("nonce diferente: quote reaproveitado de outra sessão")
    for indice, esperado in politica.items():
        atual = quote["corpo"]["pcrs"].get(str(indice))
        if atual is None:
            problemas.append(f"PCR {indice} não está no quote")
        elif atual != esperado.hex():
            problemas.append(f"PCR {indice} diferente da política: a máquina rodou algo diferente do esperado")
    return problemas


def boot_medido(tpm: TPM, componentes: list[tuple[int, bytes]]) -> None:
    """Cada componente do boot é medido no PCR dele antes de rodar."""
    for indice, codigo in componentes:
        tpm.extend(indice, codigo)


def ler_pcrs_reais(indices=(0, 7)) -> dict | None:
    """PCRs do TPM desta máquina via tpm2-tools. None quando não há TPM ou ferramenta."""
    if shutil.which("tpm2_pcrread") is None:
        return None
    sel = "sha256:" + ",".join(str(i) for i in indices)
    r = subprocess.run(["tpm2_pcrread", sel], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    saida = {}
    for linha in r.stdout.splitlines():
        linha = linha.strip()
        if ":" in linha and linha.split(":")[0].strip().isdigit():
            k, v = linha.split(":", 1)
            saida[int(k)] = v.strip().lower().removeprefix("0x")
    return saida or None


if __name__ == "__main__":
    tpm = TPM()
    boot = [(0, b"UEFI 1.2"), (0, b"opcao ROM da placa de rede"), (7, b"estado do Secure Boot: ligado"), (4, b"shim"), (4, b"grub")]
    boot_medido(tpm, boot)
    politica = {0: tpm.pcrs[0], 7: tpm.pcrs[7]}
    nonce = b"sessao-1"
    print("máquina íntegra:", verificar_quote(tpm.quote([0, 7], nonce), tpm.chave_publica_pem(), nonce, politica) or "aceita")
    outra = TPM()
    boot_medido(outra, [(0, b"UEFI 1.2 com implante"), (0, b"opcao ROM da placa de rede"), (7, b"estado do Secure Boot: ligado")])
    print("firmware alterado:", verificar_quote(outra.quote([0, 7], nonce), outra.chave_publica_pem(), nonce, politica))
    reais = ler_pcrs_reais()
    print("TPM desta máquina:", reais if reais else "não há TPM acessível ou tpm2-tools instalado (sem fingir)")
