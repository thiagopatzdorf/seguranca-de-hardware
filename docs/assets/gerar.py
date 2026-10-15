#!/usr/bin/env python3
"""Identidade visual do repositório, gerada por código — não desenhada à mão.

A mesma paleta e a mesma família do `james-theorems` (marfim #F6F1E7, grafite
#141414, ouro #B8975A), para os dois repositórios se lerem como irmãos. O motivo
é a tese do repo: **marcas soltas no caos (o que ainda não foi verificado) pousam,
uma a uma, nas células de uma fita — a cadeia de confiança — e uma célula de ouro
marca a raiz, a única provada cara, da qual tudo depois só se verifica barato.**

É *generativo*: uma `--seed` espalha as marcas e escolhe os desvios. Cada seed é um
layout diferente — infinitos layouts da mesma ideia. O que NÃO muda com a seed: a
fita, a raiz de ouro, a paleta e a mensagem. O que muda: onde o caos cai e como se
assenta. Um banner que é, ele mesmo, uma demonstração de "caos → ordem".

    python3 docs/assets/gerar.py                 # banner claro, escuro e social (seed fixa)
    python3 docs/assets/gerar.py --seed 7        # outro layout, mesma ideia
    python3 docs/assets/gerar.py --galeria 6     # 6 variações em docs/assets/galeria/, para escolher

Saída: SVG puro (geometria, sem webfont — nítido em qualquer tela e seguro dentro
de <img> no GitHub). O título vive no README, não na imagem, de propósito: a imagem
é a ideia; a palavra é do texto. Inversa: `git rm` dos arquivos em SAIDAS.
"""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

AQUI = Path(__file__).resolve().parent
LARG, ALT = 1280, 480
SAIDAS = ("banner-claro.svg", "banner-escuro.svg", "social-preview.svg")

TEMAS = {
    "claro":  {"fundo": "#F6F1E7", "tinta": "#141414", "suave": "#5C564C",
               "fraco": "#E4DBCA", "ouro": "#B8975A", "linha": "#141414"},
    "escuro": {"fundo": "#141414", "tinta": "#F6F1E7", "suave": "#A9A193",
               "fraco": "#2B2926", "ouro": "#B8975A", "linha": "#F6F1E7"},
}


def cena(tema: dict, seed: int, larg: int = LARG, alt: int = ALT) -> str:
    """Uma cena: fita de células na horizontal, raiz de ouro à esquerda, e marcas
    do caos que caem e se assentam nas células conforme a 'ordem' avança para a direita."""
    rnd = random.Random(seed)
    el = []
    def add(s): el.append(s)

    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {larg} {alt}" '
        f'width="{larg}" height="{alt}" role="img" '
        f'aria-label="Segurança de hardware: marcas soltas do caos pousam nas células de uma fita — a cadeia de confiança — a partir de uma raiz de ouro provada uma vez.">')
    add(f'<rect width="{larg}" height="{alt}" fill="{tema["fundo"]}"/>')

    # a fita: N células, centro vertical
    N = 18
    cy = alt * 0.56
    cel = larg * 0.80 / N
    ox = (larg - cel * N) / 2
    r = cel * 0.30

    # trilho da fita (linha fina)
    add(f'<line x1="{ox:.1f}" y1="{cy:.1f}" x2="{ox+cel*N:.1f}" y2="{cy:.1f}" '
        f'stroke="{tema["fraco"]}" stroke-width="2"/>')

    # caos: pontos soltos no alto, densos na FRONTEIRA (direita, o que ainda não
    # foi verificado) e rareando para a esquerda, onde a raiz de ouro já pôs ordem.
    for _ in range(300):
        gx = rnd.random() ** 0.7                 # viés para a direita
        px = ox + gx * cel * N + rnd.uniform(-cel, cel)
        banda = 0.10 + 0.40 * gx                 # faixa vertical do ruído cresce à direita
        py = cy - alt * (0.06 + rnd.random() * banda)
        if rnd.random() < 0.18 * gx:             # alguns também abaixo
            py = cy + alt * (0.04 + rnd.random() * banda * 0.6)
        rr = rnd.uniform(0.7, 1.9)
        op = 0.08 + 0.5 * gx * rnd.random()
        add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rr:.2f}" fill="{tema["suave"]}" opacity="{op:.2f}"/>')

    # células: da esquerda (ordenada, cheia) para a direita (ainda assentando)
    for i in range(N):
        x = ox + cel * (i + 0.5)
        ordem = i / (N - 1)                      # 0 = raiz, 1 = fronteira do que falta verificar
        assentou = rnd.random() > ordem * 0.92   # células à direita podem estar "em verificação"
        raiz = (i == 0)
        if raiz:
            # raiz de confiança: célula de ouro, cheia, com halo
            add(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="{r*1.5:.1f}" fill="{tema["ouro"]}" opacity="0.16"/>')
            add(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{tema["ouro"]}"/>')
            continue
        # elo verificado liga a célula anterior a esta
        xp = ox + cel * (i - 0.5)
        if assentou:
            add(f'<line x1="{xp:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{cy:.1f}" '
                f'stroke="{tema["linha"]}" stroke-width="2.2" opacity="{0.9-0.5*ordem:.2f}"/>')
            add(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" '
                f'stroke="{tema["linha"]}" stroke-width="2"/>')
            # ponto interno: preenchido = conteúdo verificado
            add(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="{r*0.42:.1f}" fill="{tema["linha"]}" opacity="0.8"/>')
            # uma marca do caos "caindo" na direção desta célula
            if rnd.random() < 0.5:
                fx = x + rnd.uniform(-cel*0.3, cel*0.3)
                fy = cy - alt * (0.08 + rnd.random()*0.14)
                add(f'<line x1="{fx:.1f}" y1="{fy:.1f}" x2="{x:.1f}" y2="{cy-r:.1f}" '
                    f'stroke="{tema["ouro"]}" stroke-width="1.2" opacity="0.5"/>')
        else:
            # ainda não assentou: célula tracejada, vazia (a fronteira do que falta verificar)
            add(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" '
                f'stroke="{tema["suave"]}" stroke-width="1.6" stroke-dasharray="3 4" opacity="0.7"/>')

    add('</svg>')
    return "\n".join(el)


def escrever(destino: Path, seed: int, social: bool = False):
    for nome, tema in (("banner-claro.svg", "claro"), ("banner-escuro.svg", "escuro")):
        (destino / nome).write_text(cena(TEMAS[tema], seed), encoding="utf-8")
    # social preview: proporção 2:1, fundo escuro (o que o GitHub/Twitter mostram)
    (destino / "social-preview.svg").write_text(cena(TEMAS["escuro"], seed, 1280, 640), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=314159, help="semente do layout (cada uma é um layout)")
    ap.add_argument("--galeria", type=int, default=0, help="gera N variações em docs/assets/galeria/ e sai")
    args = ap.parse_args()
    if args.galeria:
        g = AQUI / "galeria"; g.mkdir(exist_ok=True)
        for s in range(args.galeria):
            (g / f"escuro-{s}.svg").write_text(cena(TEMAS["escuro"], s), encoding="utf-8")
            (g / f"claro-{s}.svg").write_text(cena(TEMAS["claro"], s), encoding="utf-8")
        print(f"{args.galeria} variações em {g} (claro e escuro de cada seed)")
    else:
        escrever(AQUI, args.seed)
        print("gerado:", ", ".join(SAIDAS), f"(seed {args.seed})")
