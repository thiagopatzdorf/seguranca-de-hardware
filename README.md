# Segurança de hardware: princípios e laboratórios

Uma trilha prática de segurança de hardware, com os princípios escritos e
cada princípio acompanhado de código que você roda, quebra e conserta.
Feita para o **Pedro Araújo** (técnico de informática, infraestrutura e
redes, segurança da informação, Brusque, SC), a partir do ponto em que ele
já está: Google Cybersecurity, IBSEC, Linux e SQL. Serve para qualquer
pessoa no mesmo caminho.

A ideia que atravessa tudo: **software confia em hardware, e hardware só
merece confiança quando pode ser verificado.** Cada laboratório mostra uma
forma de verificar, e uma forma de burlar quando a verificação falta.

## Mapa

| | o que é | o que você aprende |
|---|---|---|
| [PRINCIPIOS.md](PRINCIPIOS.md) | os dez princípios, cada um com o ataque que ele impede | o porquê |
| [CHECKLIST.md](CHECKLIST.md) | endurecimento de uma máquina real, item por item, com o comando que prova | o como |
| [TRILHA.md](TRILHA.md) | ordem de estudo, do que o Pedro já tem até o próximo passo | o quando |
| `labs/01-cadeia-de-confianca` | boot seguro simulado: ROM → bootloader → kernel, cada estágio assina o próximo | raiz e cadeia de confiança |
| `labs/02-canal-lateral-tempo` | a comparação de senha que vaza pelo relógio, medida de verdade | canais laterais |
| `labs/03-atestacao-tpm` | PCRs, `extend` e *quote* como o TPM faz; verificador de política | atestação |
| `labs/04-inventario-usb` | inventário de USB pelo `/sys` e detecção de teclado que aparece sozinho (BadUSB) | acesso físico |
| `labs/05-integridade-firmware` | manifesto de hashes do `/boot` e verificação que pega troca de arquivo | firmware é software |
| `labs/06-memoria` | quais defesas de memória um binário tem (NX, PIE, canário) e cópia de string segura | por que o hardware precisa ajudar a memória |
| `ferramentas/avaliar.py` | o avaliador: mede a máquina (Secure Boot, TPM, IOMMU, disco cifrado) e dá nota com motivo | medir antes de afirmar |

## Rodar

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q                      # todos os laboratórios, sem precisar de hardware especial
python3 ferramentas/avaliar.py # a nota da máquina em que você está (Linux)
```

Cada laboratório tem o próprio `README.md` com o que rodar e o que observar.
Nenhum exige TPM, placa especial ou acesso de root para os testes; onde o
hardware real existe (TPM em `/dev/tpm0`, EFI em `/sys/firmware/efi`), o
código o usa; onde não existe, diz que não existe em vez de fingir.

## Regras do repositório

- **Meça antes de afirmar.** Toda afirmação de segurança aqui vem com o
  comando ou o teste que a prova.
- **Teste com nome que descreve a falha.** `test_imagem_alterada_nao_boota`,
  não `test_boot`.
- **Nada de segredo em código.** Chaves dos laboratórios são geradas na hora
  e descartadas.
- **Ataque e defesa no mesmo arquivo.** Entender a defesa sem ver o ataque é
  decorar; ver os dois é aprender.

## Contribuir

Issue ou PR em português, pequeno, com teste. Erro encontrado é bem-vindo:
é a medida mais barata de onde falta uma regra.
