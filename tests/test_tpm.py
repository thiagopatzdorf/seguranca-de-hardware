import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "labs" / "03-atestacao-tpm"))

from tpm import TPM, ZERO, boot_medido, extend, verificar_quote  # noqa: E402


def test_extend_nao_tem_inverso_e_muda_sempre():
    a = extend(ZERO, b"UEFI")
    b = extend(a, b"grub")
    assert a != ZERO and b != a
    assert len(a) == 32


def test_ordem_diferente_da_mesma_medida_da_pcr_diferente():
    # extend(x) depois extend(y) != extend(y) depois extend(x): a sequência importa.
    um = extend(extend(ZERO, b"A"), b"B")
    dois = extend(extend(ZERO, b"B"), b"A")
    assert um != dois


def test_maquina_integra_passa_na_politica():
    tpm = TPM()
    boot_medido(tpm, [(0, b"UEFI"), (7, b"secure boot on")])
    politica = {0: tpm.pcrs[0], 7: tpm.pcrs[7]}
    nonce = b"n1"
    problemas = verificar_quote(tpm.quote([0, 7], nonce), tpm.chave_publica_pem(), nonce, politica)
    assert problemas == []


def test_firmware_alterado_falha_na_politica():
    bom = TPM()
    boot_medido(bom, [(0, b"UEFI")])
    politica = {0: bom.pcrs[0]}
    ruim = TPM()
    boot_medido(ruim, [(0, b"UEFI com implante")])
    nonce = b"n1"
    problemas = verificar_quote(ruim.quote([0], nonce), ruim.chave_publica_pem(), nonce, politica)
    assert any("PCR 0" in p for p in problemas)


def test_quote_reaproveitado_de_outra_sessao_e_recusado():
    tpm = TPM()
    boot_medido(tpm, [(0, b"UEFI")])
    politica = {0: tpm.pcrs[0]}
    quote = tpm.quote([0], b"nonce-antigo")
    problemas = verificar_quote(quote, tpm.chave_publica_pem(), b"nonce-novo", politica)
    assert any("nonce" in p for p in problemas)


def test_quote_de_outro_tpm_nao_passa_pela_chave_publica():
    tpm = TPM()
    boot_medido(tpm, [(0, b"UEFI")])
    outro = TPM()
    quote_do_outro = outro.quote([0], b"n")
    problemas = verificar_quote(quote_do_outro, tpm.chave_publica_pem(), b"n", {0: tpm.pcrs[0]})
    assert any("assinatura" in p for p in problemas)
