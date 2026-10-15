# 06. Memória: por que o hardware precisa ajudar

Em C, nada na linguagem impede um programa de escrever fora de um buffer.
Quem segura são o compilador e o processador, com camadas que se somam:

| defesa | o que faz | de quem é |
|---|---|---|
| **NX** (bit de não-execução) | dados na pilha não podem ser executados como código | processador (MMU) |
| **PIE + ASLR** | os endereços mudam a cada execução, então um endereço fixo não serve | SO + processador |
| **canário de pilha** | um valor entre o buffer e o endereço de retorno; se mudou, aborta | compilador |
| **RELRO** | a tabela de ligação vira somente-leitura depois de carregada | ligador + SO |
| **FORTIFY** | o compilador recusa cópias cujo estouro ele consegue provar | compilador + glibc |

## Ver as defesas de um binário

```bash
python3 protecoes.py "$(command -v ls)"
```

Diagnóstico puro: lê os cabeçalhos ELF com `readelf` e diz o que o binário
carrega. Rode nos programas do seu sistema e veja que quase todos já têm NX,
PIE e canário: a defesa está ligada por padrão, e é bom saber reconhecer.

## Ver a cópia segura

```bash
cc -O2 -D_FORTIFY_SOURCE=2 -fstack-protector-strong -o strings_seguras strings_seguras.c
./strings_seguras "cabe"
./strings_seguras "um texto bem maior que o destino de 16 bytes"
python3 protecoes.py ./strings_seguras
```

`strings_seguras.c` mostra como copiar uma string sem nunca passar do fim
do buffer (tamanho explícito, terminador garantido, aviso no corte). É o
hábito que torna o canário e o FORTIFY uma rede de segurança, não a única
linha de defesa.

Nenhum arquivo aqui contém código de exploração. O objetivo é reconhecer e
ligar as defesas, que é o trabalho de quem opera e endurece máquinas.
