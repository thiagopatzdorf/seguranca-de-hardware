# 01. Cadeia de confiança

```bash
python3 cadeia.py
```

O que acontece:

1. A "fábrica" gera a chave da ROM e grava só a parte pública na ROM.
2. A ROM verifica o bootloader; o bootloader carrega a chave pública do
   kernel; o kernel é verificado com ela.
3. Um byte alterado no kernel: a assinatura não bate, o boot para, e o
   registro diz onde parou.

Perguntas para responder com o código, não de cabeça:

- Se você trocar a chave pública do kernel dentro do bootloader (sem
  reassinar o bootloader), por que a ROM recusa? Veja `conteudo_assinado`.
- O que acontece se a chave privada da ROM vazar? (Resposta: tudo. É por
  isso que ela fica num HSM na fábrica e nunca numa máquina de
  desenvolvedor.)
- Onde está o Secure Boot de verdade nisto? UEFI = ROM; shim/GRUB =
  bootloader; vmlinuz = kernel; a chave da ROM = `db` do firmware.
