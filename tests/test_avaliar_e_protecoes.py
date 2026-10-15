import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas"))
sys.path.insert(0, str(RAIZ / "labs" / "06-memoria"))

import avaliar  # noqa: E402
import protecoes  # noqa: E402


def test_a_nota_e_determinada_pelos_pesos_e_nunca_passa_de_100():
    itens = avaliar.medir()
    assert itens, "o avaliador não mediu nada"
    n = avaliar.nota(itens)
    assert 0 <= n <= 100


def test_item_nao_medido_conta_como_ausente_nao_como_aprovado():
    # Princípio 10: o que não dá para medir não vira ponto.
    item = avaliar.Item("x", 20, None, "não medido")
    assert item.pontos == 0


def test_a_foto_tem_os_campos_que_a_comparacao_do_mes_seguinte_precisa():
    f = avaliar.foto(avaliar.medir())
    for campo in ("quando", "maquina", "nota", "itens"):
        assert campo in f


def test_protecoes_le_um_binario_do_sistema_e_reconhece_as_defesas():
    if shutil.which("readelf") is None:
        pytest.skip("readelf ausente")
    alvo = Path(shutil.which("true") or "/bin/true")
    p = protecoes.protecoes(alvo)
    assert "ferramenta" not in p, p
    # binários de distribuição modernos trazem NX ligado
    assert p["nx"] is True
    assert isinstance(protecoes.resumo(p), str)


def test_strings_seguras_compila_e_trunca_a_entrada_grande():
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        pytest.skip("sem compilador C")
    fonte = RAIZ / "labs" / "06-memoria" / "strings_seguras.c"
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        binario = Path(d) / "s"
        r = subprocess.run([cc, "-O2", "-D_FORTIFY_SOURCE=2", "-fstack-protector-strong",
                            "-o", str(binario), str(fonte)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        curto = subprocess.run([str(binario), "cabe"], capture_output=True, text=True)
        assert "truncado" not in curto.stdout
        grande = subprocess.run([str(binario), "x" * 100], capture_output=True, text=True)
        assert grande.returncode == 0 and "truncado" in grande.stdout
        # e o binário carrega as defesas que pedimos ao compilador
        if shutil.which("readelf"):
            p = protecoes.protecoes(binario)
            assert p["canario"] is True
