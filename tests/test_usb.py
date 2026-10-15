import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "labs" / "04-inventario-usb"))

from usb import comparar, listar  # noqa: E402


def _dispositivo(raiz: Path, nome: str, vendor: str, produto: str, classe: str, serial: str = ""):
    """Monta no disco uma árvore de sysfs falsa para um dispositivo e sua interface."""
    d = raiz / nome
    d.mkdir()
    (d / "idVendor").write_text(vendor)
    (d / "idProduct").write_text(produto)
    (d / "manufacturer").write_text("Fabricante")
    (d / "product").write_text("Produto")
    if serial:
        (d / "serial").write_text(serial)
    iface = raiz / f"{nome}:1.0"
    iface.mkdir()
    (iface / "bInterfaceClass").write_text(classe)


def test_listar_le_do_sysfs_falso_sem_depender_da_maquina(tmp_path):
    _dispositivo(tmp_path, "1-1", "0781", "5583", "08", serial="AA")  # pendrive (armazenamento)
    disp = listar(tmp_path)
    assert len(disp) == 1
    assert disp[0].classes == ("08",)
    assert not disp[0].e_hid


def test_teclado_e_reconhecido_como_hid(tmp_path):
    _dispositivo(tmp_path, "1-2", "046d", "c31c", "03", serial="KB")
    assert listar(tmp_path)[0].e_hid


def test_hid_que_aparece_sozinho_e_sinalizado(tmp_path):
    antes = tmp_path / "antes"
    depois = tmp_path / "depois"
    antes.mkdir()
    depois.mkdir()
    _dispositivo(antes, "1-1", "0781", "5583", "08", serial="AA")
    _dispositivo(depois, "1-1", "0781", "5583", "08", serial="AA")
    _dispositivo(depois, "1-3", "dead", "beef", "03", serial="XX")  # "teclado" novo = BadUSB
    r = comparar(listar(antes), listar(depois))
    assert len(r["hid_novo"]) == 1
    assert r["hid_novo"][0].fabricante_id == "dead"


def test_pendrive_novo_de_armazenamento_nao_dispara_alerta_de_hid(tmp_path):
    antes = tmp_path / "a"
    depois = tmp_path / "b"
    antes.mkdir()
    depois.mkdir()
    _dispositivo(depois, "1-4", "0781", "0001", "08", serial="NOVO")
    r = comparar(listar(antes), listar(depois))
    assert len(r["novos"]) == 1 and r["hid_novo"] == []


def test_sysfs_ausente_devolve_lista_vazia_sem_quebrar(tmp_path):
    assert listar(tmp_path / "nao-existe") == []
