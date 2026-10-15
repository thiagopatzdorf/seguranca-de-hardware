import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "labs" / "05-integridade-firmware"))

from manifesto import gerar, integro, verificar  # noqa: E402


def _boot_falso(raiz: Path):
    raiz.mkdir()
    (raiz / "vmlinuz-6.1").write_bytes(b"kernel")
    (raiz / "initrd.img").write_bytes(b"initrd")
    sub = raiz / "grub"
    sub.mkdir()
    (sub / "grub.cfg").write_bytes(b"menuentry ...")


def test_manifesto_recem_gerado_confere_consigo_mesmo(tmp_path):
    boot = tmp_path / "boot"
    _boot_falso(boot)
    m = gerar(boot)
    assert len(m) == 3
    assert integro(verificar(boot, m))


def test_arquivo_alterado_e_detectado(tmp_path):
    boot = tmp_path / "boot"
    _boot_falso(boot)
    m = gerar(boot)
    (boot / "vmlinuz-6.1").write_bytes(b"kernel trocado")
    r = verificar(boot, m)
    assert r["alterados"] == ["vmlinuz-6.1"]
    assert not integro(r)


def test_arquivo_removido_e_arquivo_novo_sao_detectados(tmp_path):
    boot = tmp_path / "boot"
    _boot_falso(boot)
    m = gerar(boot)
    (boot / "initrd.img").unlink()
    (boot / "backdoor.efi").write_bytes(b"x")
    r = verificar(boot, m)
    assert r["sumiram"] == ["initrd.img"]
    assert r["novos"] == ["backdoor.efi"]


def test_troca_de_conteudo_mantendo_o_tamanho_ainda_e_pega(tmp_path):
    # Hash, não tamanho: trocar byte por byte sem mudar o tamanho não engana.
    boot = tmp_path / "boot"
    _boot_falso(boot)
    m = gerar(boot)
    (boot / "initrd.img").write_bytes(b"XXXXXX")  # mesmo tamanho de "initrd"
    assert verificar(boot, m)["alterados"] == ["initrd.img"]
