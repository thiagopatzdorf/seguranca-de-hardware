"""Canal lateral de tempo: a comparação que vaza pelo relógio.

`comparar_ingenuo` para no primeiro byte diferente. Quanto mais bytes
certos o atacante acerta, mais tempo a função demora. Medindo o tempo, ele
descobre o segredo byte a byte, em vez de tentar todas as combinações.

`comparar_constante` (hmac.compare_digest) demora o mesmo tempo sempre.

    python3 comparar.py        # mede as duas e mostra o vazamento (ou a ausência dele)
"""
from __future__ import annotations

import hmac
import statistics
import time


def comparar_ingenuo(a: bytes, b: bytes) -> bool:
    """Como quase todo mundo escreve a primeira vez. NÃO use para segredo."""
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x != y:
            return False  # <- aqui está o vazamento: sai cedo
    return True


def comparar_constante(a: bytes, b: bytes) -> bool:
    return hmac.compare_digest(a, b)


def tempo_mediano_ns(funcao, segredo: bytes, tentativa: bytes, repeticoes: int = 20000) -> float:
    """Mediana de muitas medições: o ruído do sistema é grande, a mediana o doma."""
    amostras = []
    for _ in range(repeticoes):
        inicio = time.perf_counter_ns()
        funcao(segredo, tentativa)
        amostras.append(time.perf_counter_ns() - inicio)
    return statistics.median(amostras)


def tentativa_com_prefixo_certo(segredo: bytes, bytes_certos: int) -> bytes:
    """Os primeiros `bytes_certos` iguais ao segredo, o resto errado."""
    errado = bytes((b ^ 0xFF) for b in segredo[bytes_certos:])
    return segredo[:bytes_certos] + errado


def perfil(funcao, segredo: bytes, repeticoes: int = 20000) -> list[float]:
    """Tempo mediano para 0, 1, 2, ... bytes certos no prefixo."""
    return [tempo_mediano_ns(funcao, segredo, tentativa_com_prefixo_certo(segredo, n), repeticoes)
            for n in range(len(segredo) + 1)]


def inclinacao(perfil_ns: list[float]) -> float:
    """Quanto o tempo cresce por byte certo (regressão linear simples). Perto de zero = sem vazamento."""
    n = len(perfil_ns)
    xs = list(range(n))
    mx, my = statistics.mean(xs), statistics.mean(perfil_ns)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, perfil_ns))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else 0.0


if __name__ == "__main__":
    segredo = b"s3gr3d0-de-32-bytes-para-medir!!"
    for nome, f in (("ingênua", comparar_ingenuo), ("constante", comparar_constante)):
        p = perfil(f, segredo, repeticoes=5000)
        print(f"{nome:10s} inclinação {inclinacao(p):+.1f} ns por byte certo  "
              f"| 0 certos {p[0]:.0f} ns, {len(segredo)} certos {p[-1]:.0f} ns")
