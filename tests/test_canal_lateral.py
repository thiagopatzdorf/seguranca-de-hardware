import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "labs" / "02-canal-lateral-tempo"))

from comparar import (  # noqa: E402
    comparar_constante,
    comparar_ingenuo,
    inclinacao,
    perfil,
    tentativa_com_prefixo_certo,
)

SEGREDO = b"s3gr3d0-de-32-bytes-para-medir!!"


def test_as_duas_comparacoes_dao_a_resposta_certa():
    assert comparar_ingenuo(SEGREDO, SEGREDO) is True
    assert comparar_constante(SEGREDO, SEGREDO) is True
    errado = tentativa_com_prefixo_certo(SEGREDO, 4)
    assert comparar_ingenuo(SEGREDO, errado) is False
    assert comparar_constante(SEGREDO, errado) is False


def test_prefixo_certo_tem_o_tamanho_do_segredo():
    t = tentativa_com_prefixo_certo(SEGREDO, 5)
    assert len(t) == len(SEGREDO)
    assert t[:5] == SEGREDO[:5] and t[5] != SEGREDO[5]


def test_a_comparacao_ingenua_vaza_mais_tempo_que_a_constante():
    # A ingênua cresce com bytes certos; a constante não. Medimos a inclinação
    # das duas e exigimos que a ingênua inclíne bem mais. Tolerante ao ruído
    # do agendador: comparamos uma com a outra, não contra um valor absoluto.
    reps = 4000
    ing = inclinacao(perfil(comparar_ingenuo, SEGREDO, reps))
    const = inclinacao(perfil(comparar_constante, SEGREDO, reps))
    assert ing > abs(const) * 3, f"ingênua={ing:.1f} ns/byte, constante={const:.1f} ns/byte"
    assert ing > 0
