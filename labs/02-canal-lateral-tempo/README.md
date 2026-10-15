# 02. Canal lateral de tempo

```bash
python3 comparar.py
```

Saída esperada (os números mudam de máquina para máquina; a forma, não):

```
ingênua    inclinação +18.3 ns por byte certo | 0 certos 190 ns, 32 certos 780 ns
constante  inclinação  +0.2 ns por byte certo | 0 certos 160 ns, 32 certos 165 ns
```

A ingênua demora mais quanto mais bytes o atacante acerta: é o relógio
entregando o segredo. A constante não.

Por que importa em hardware: o mesmo princípio vale para consumo de
energia (análise diferencial de potência em cartões inteligentes), para
cache (Spectre, Meltdown) e para emissão eletromagnética. A regra: nada que
dependa do segredo pode mudar o tempo, o caminho ou o consumo.

Onde procurar no seu código: qualquer `==` entre token, hash ou senha.
Troque por `hmac.compare_digest`.
