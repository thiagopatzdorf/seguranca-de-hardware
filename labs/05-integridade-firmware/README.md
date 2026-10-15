# 05. Integridade de firmware e do boot

```bash
python3 manifesto.py gerar /boot manifesto-boot.json
python3 manifesto.py verificar /boot manifesto-boot.json   # sai 0 se íntegro, 1 se não
```

Depois de uma atualização de kernel, o `verificar` vai apontar arquivos
novos e alterados: isso é esperado, e é o momento de gerar o manifesto de
novo. Alteração **sem** atualização é o sinal.

Para firmware de verdade: com `flashrom` dá para ler a imagem da BIOS
(`flashrom -p internal -r bios.bin`, com cuidado e lendo a documentação
da sua placa). Gere o manifesto da pasta onde guarda os dumps e compare
entre leituras.

Limite honesto: um atacante com root pode alterar o arquivo E o manifesto.
Por isso o manifesto vai para fora da máquina, e por isso o TPM
(laboratório 03) existe: lá a medida fica num lugar que root não reescreve.
