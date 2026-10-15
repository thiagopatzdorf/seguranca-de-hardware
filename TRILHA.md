# Trilha de estudo

Ponto de partida (o que o Pedro já tem): Google Cybersecurity Professional
Certificate, Fundamentos em Cibersegurança (IBSEC), simulação Mastercard,
Linux e SQL, suporte técnico, redes e manutenção de computadores.

Esse último item é a vantagem: quem já abriu gabinete, trocou disco e
configurou BIOS tem a intuição física que falta a muita gente de software.
A trilha transforma essa intuição em verificação.

## Semana 1: a cadeia de confiança

1. Ler `PRINCIPIOS.md`, 1 a 3.
2. Rodar `labs/01-cadeia-de-confianca`: ver o boot passar, alterar um byte
   do kernel, ver o boot recusar. Depois trocar a chave do bootloader e
   responder: por que a ROM recusa?
3. Na sua máquina: `mokutil --sb-state`. Está ligado? Se não, por quê?

## Semana 2: medir sem confiar

1. `labs/03-atestacao-tpm`: entender PCR e `extend` com papel e caneta
   antes de rodar (o teste `test_ordem_diferente_da_mesma_medida_da_pcr_diferente`
   é a chave).
2. Se a máquina tiver TPM: `tpm2_pcrread sha256:0,7` (pacote `tpm2-tools`)
   e comparar depois de uma atualização de BIOS.
3. Ler sobre Measured Boot e o que o Windows faz com BitLocker + TPM.

## Semana 3: o que vaza

1. `labs/02-canal-lateral-tempo`: rodar `comparar.py` e ver a inclinação
   do tempo por byte certo. Depois trocar por `hmac.compare_digest` e ver
   o vazamento sumir.
2. Procurar no próprio código (ou no de um projeto open source) uma
   comparação de token com `==`. Abrir issue ou PR.

## Semana 4: a mão na máquina

1. `labs/04-inventario-usb`: rodar o inventário, plugar um teclado, rodar
   de novo. Instalar a regra udev e testar.
2. `CHECKLIST.md` inteiro na sua máquina, com `ferramentas/avaliar.py`.
   Anotar a nota. Consertar o item mais barato. Medir de novo.
3. Ler sobre IOMMU e ataques de DMA (Thunderclap, PCILeech).

## Semana 5: firmware e memória

1. `labs/05-integridade-firmware`: gerar o manifesto do `/boot`, atualizar
   o kernel, verificar, entender a diferença.
2. `labs/06-memoria`: usar `protecoes.py` nos binários do sistema; compilar
   `strings_seguras.c` e ver a cópia que trunca em vez de estourar. Ler
   sobre NX, ASLR e *shadow stack* (CET).

## Depois

- **Certificação que conversa com isto**: CompTIA Security+ (domínio de
  segurança física e criptografia em hardware) e, mais à frente, GIAC
  GSEC. Para hardware de verdade: cursos de firmware/UEFI e o livro
  *Rootkits and Bootkits* (Matrosov, Rodionov, Bratus).
- **Projeto para o portfólio**: pegar uma máquina velha, aplicar o
  checklist inteiro, registrar antes/depois com o `avaliar.py` e publicar
  o relatório. Vale mais que um certificado, porque é medido.
- **Ferramentas para conhecer**: `tpm2-tools`, `fwupd`, `usbguard`,
  `boltctl`, `chipsec` (auditoria de plataforma), `flashrom` (ler firmware
  de verdade, com cuidado).
