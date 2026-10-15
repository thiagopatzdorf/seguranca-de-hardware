# Como contribuir

Toda mudança entra com teste que falha sem ela, e o nome do teste descreve a
falha (`test_firmware_alterado_falha_na_politica`, não `test_tpm`). Abra
issue ou PR em português; pequeno é melhor que completo.

Rodar antes de abrir:

```bash
pip install -r requirements.txt
pytest -q
```

Nada de segredo, chave ou caminho de máquina em código. Os laboratórios
geram as chaves de que precisam na hora e as descartam.

Achou um erro? É bem-vindo: erro é a medida mais barata de onde falta uma
regra. Descreva o defeito (o que esperava, o que aconteceu, como reproduzir),
não quem errou.
