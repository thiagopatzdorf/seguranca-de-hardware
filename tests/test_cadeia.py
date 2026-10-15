import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "labs" / "01-cadeia-de-confianca"))

from cadeia import BootRecusado, alterar_um_byte, montar_cadeia  # noqa: E402

import pytest  # noqa: E402


def test_cadeia_integra_boota_ate_o_kernel():
    rom, imagens, _ = montar_cadeia()
    registro = rom.bootar(imagens)
    assert registro == ["bootloader: ok", "kernel: ok"]


def test_um_byte_no_kernel_interrompe_o_boot():
    rom, imagens, _ = montar_cadeia()
    adulteradas = [imagens[0], alterar_um_byte(imagens[1])]
    with pytest.raises(BootRecusado, match="kernel"):
        rom.bootar(adulteradas)
    assert rom.registro[-1].endswith("boot interrompido")


def test_bootloader_alterado_para_antes_de_chegar_ao_kernel():
    rom, imagens, _ = montar_cadeia()
    adulteradas = [alterar_um_byte(imagens[0]), imagens[1]]
    with pytest.raises(BootRecusado, match="bootloader"):
        rom.bootar(adulteradas)
    assert "kernel: ok" not in rom.registro  # falha cedo: o kernel nem é avaliado


def test_trocar_a_chave_do_proximo_estagio_sem_reassinar_derruba_a_cadeia():
    # A assinatura do bootloader cobre a chave pública do kernel; trocá-la invalida tudo.
    rom, imagens, chaves = montar_cadeia()
    _, outra_cadeia, _ = montar_cadeia()
    bootloader_falso = imagens[0].__class__(
        imagens[0].nome, imagens[0].codigo, imagens[0].assinatura,
        outra_cadeia[0].proxima_chave_publica)  # chave do kernel de outra cadeia
    with pytest.raises(BootRecusado):
        rom.bootar([bootloader_falso, imagens[1]])


def test_a_chave_da_rom_nao_muda_depois_de_criada():
    rom, _, _ = montar_cadeia()
    assert hasattr(rom, "chave_publica_pem")
    # a ROM não oferece um método para trocar a chave: é a raiz de confiança
    assert not hasattr(rom, "trocar_chave")
