"""Boot seguro simulado: ROM -> bootloader -> kernel.

A ROM é a raiz de confiança: carrega UMA chave pública gravada "em silício"
(aqui, um atributo que ninguém reescreve depois de criada). Cada estágio
só passa o controle ao próximo depois de verificar a assinatura dele.

    python3 cadeia.py          # monta uma cadeia, boota, altera um byte, vê recusar

O que este arquivo mostra: verificar é barato (uma chave pública, um Ed25519
verify), gerar é caro (a chave privada fica com quem constrói), e um byte
diferente na imagem derruba a cadeia inteira.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


@dataclass(frozen=True)
class Imagem:
    """Um estágio de boot: o código, quem o assinou e a chave pública do estágio seguinte."""

    nome: str
    codigo: bytes
    assinatura: bytes
    proxima_chave_publica: bytes | None = None  # PEM; None no último estágio

    def conteudo_assinado(self) -> bytes:
        # A assinatura cobre o código E a chave do próximo estágio: trocar a
        # chave seguinte sem reassinar também derruba a cadeia.
        return hashlib.sha256(self.codigo + (self.proxima_chave_publica or b"")).digest()


class BootRecusado(Exception):
    pass


@dataclass
class ROM:
    """Raiz de confiança. A chave pública entra na criação e não muda."""

    chave_publica_pem: bytes
    registro: list[str] = field(default_factory=list)

    def bootar(self, imagens: list[Imagem]) -> list[str]:
        """Verifica estágio por estágio. Qualquer falha para tudo (falhe fechado)."""
        chave_atual = self.chave_publica_pem
        self.registro = []
        for imagem in imagens:
            publica = serialization.load_pem_public_key(chave_atual)
            assert isinstance(publica, Ed25519PublicKey)
            try:
                publica.verify(imagem.assinatura, imagem.conteudo_assinado())
            except InvalidSignature as e:
                self.registro.append(f"{imagem.nome}: assinatura inválida, boot interrompido")
                raise BootRecusado(imagem.nome) from e
            self.registro.append(f"{imagem.nome}: ok")
            if imagem.proxima_chave_publica is None:
                break
            chave_atual = imagem.proxima_chave_publica
        return self.registro


def pem(chave: Ed25519PrivateKey) -> bytes:
    return chave.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )


def assinar(nome: str, codigo: bytes, chave_do_estagio_anterior: Ed25519PrivateKey,
            proxima: Ed25519PrivateKey | None) -> Imagem:
    """Quem assina o estágio N é a chave cujo par público está no estágio N-1."""
    proxima_pem = pem(proxima) if proxima else None
    rascunho = Imagem(nome, codigo, b"", proxima_pem)
    return Imagem(nome, codigo, chave_do_estagio_anterior.sign(rascunho.conteudo_assinado()), proxima_pem)


def montar_cadeia(codigo_bootloader: bytes = b"bootloader v1", codigo_kernel: bytes = b"kernel 6.x"):
    """Fábrica: gera as chaves, grava a da ROM, assina bootloader e kernel."""
    chave_rom = Ed25519PrivateKey.generate()        # só a fábrica tem
    chave_bootloader = Ed25519PrivateKey.generate()  # só quem publica bootloader tem
    rom = ROM(pem(chave_rom))
    bootloader = assinar("bootloader", codigo_bootloader, chave_rom, chave_bootloader)
    kernel = assinar("kernel", codigo_kernel, chave_bootloader, None)
    return rom, [bootloader, kernel], {"rom": chave_rom, "bootloader": chave_bootloader}


def alterar_um_byte(imagem: Imagem) -> Imagem:
    codigo = bytearray(imagem.codigo)
    codigo[0] ^= 0x01
    return Imagem(imagem.nome, bytes(codigo), imagem.assinatura, imagem.proxima_chave_publica)


if __name__ == "__main__":
    rom, imagens, _ = montar_cadeia()
    print("cadeia íntegra:", " -> ".join(rom.bootar(imagens)))
    adulteradas = [imagens[0], alterar_um_byte(imagens[1])]
    try:
        rom.bootar(adulteradas)
    except BootRecusado as e:
        print("um byte alterado no kernel:", " -> ".join(rom.registro), f"(recusado em {e})")
