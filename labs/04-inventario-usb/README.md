# 04. Inventário de USB e BadUSB

```bash
python3 usb.py --salvar      # a foto do que está plugado agora
# plugue algo
python3 usb.py --comparar    # o que mudou; sai com código 2 se entrou um HID novo
```

BadUSB é um dispositivo que se apresenta como teclado e digita comandos
mais rápido do que você lê. O sistema não tem como saber que não é você.
O que ele tem como saber é que **um teclado novo apareceu**, e é isso que
este inventário vigia.

A regra udev `99-bloquear-hid-desconhecido.rules` leva isso adiante: HID
que não está na lista nem chega a funcionar. Leia o cabeçalho dela antes
de instalar; a inversa está lá.

O código lê o `/sys` direto, sem `lsusb` e sem root. A árvore é um
parâmetro, e o teste usa uma árvore falsa: nenhum teste aqui depende do
que está plugado na sua máquina.
