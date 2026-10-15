# Os dez princípios

Cada princípio vem com o ataque que ele impede e com o laboratório onde
você o vê funcionar. A ordem importa: os primeiros sustentam os seguintes.

## 1. Toda confiança começa em algo que não pode ser alterado

Software não consegue se verificar sozinho: quem verifica pode estar
comprometido. A cadeia precisa começar numa **raiz de confiança** gravada
em silício, uma ROM ou um *fuse* que ninguém reescreve depois da fábrica.
Dali, cada estágio verifica o próximo antes de lhe passar o controle.

- Ataque impedido: bootkit que troca o bootloader e carrega um kernel
  modificado antes do antivírus existir.
- Laboratório: `labs/01-cadeia-de-confianca`.

## 2. Verificar é mais barato que gerar, e é por isso que funciona

Assinar uma imagem custa uma chave privada e tempo. Verificar custa uma
chave pública e microssegundos. Um sistema seguro é desenhado para que o
lado caro fique com quem constrói e o lado barato com quem executa, em
toda inicialização.

- Ataque impedido: imagem de firmware "quase igual" com um byte a mais.
- Laboratório: `labs/01-cadeia-de-confianca` (a imagem alterada não boota)
  e `labs/05-integridade-firmware`.

## 3. Medir não é o mesmo que impedir

Secure Boot **impede** (recusa o que não está assinado). O TPM **mede**
(registra o hash de cada coisa que rodou, numa sequência que não dá para
desfazer). Os dois se completam: impedir protege a máquina; medir permite
que outra máquina (um servidor, um verificador) saiba o que esta rodou.

- Ataque impedido: máquina com boot alterado se passando por íntegra numa
  rede corporativa.
- Laboratório: `labs/03-atestacao-tpm`.

## 4. O hardware vaza pelo que não está na especificação

Tempo, consumo de energia, emissão eletromagnética, uso de cache: tudo que
varia com o segredo entrega o segredo. Um código correto na lógica pode
estar errado no relógio.

- Ataque impedido: descobrir uma senha byte a byte medindo quanto tempo a
  comparação demora.
- Laboratório: `labs/02-canal-lateral-tempo`.

## 5. Quem tem a mão na máquina tem quase tudo

Porta USB, Thunderbolt, PCIe, JTAG, UART, o próprio disco fora do gabinete:
cada um é uma entrada que ignora a senha do sistema. Defesa física não é
cadeado só; é reduzir o que uma porta pode fazer (IOMMU, bloqueio de DMA,
desligar o que não se usa) e cifrar o que fica em repouso.

- Ataques impedidos: BadUSB (um "pen drive" que é um teclado), DMA por
  Thunderbolt lendo a RAM, disco retirado e lido em outra máquina.
- Laboratórios: `labs/04-inventario-usb`, `CHECKLIST.md`.

## 6. Firmware é software, só que mais velho e menos vigiado

BIOS/UEFI, controladoras de disco, placas de rede, teclados: tudo roda
código, raramente atualizado, com privilégio maior que o do sistema
operacional. Trate como software: inventário, versão, assinatura,
atualização.

- Ataque impedido: implante persistente em UEFI que sobrevive a formatar
  o disco.
- Laboratório: `labs/05-integridade-firmware`.

## 7. A memória precisa que o hardware a defenda

Um estouro de buffer é um programa escrevendo onde não devia. A linguagem
não impede (em C), então o processador e o compilador ajudam: bit NX
(dados não executam), ASLR, canário de pilha, *shadow stack*. Nenhum
resolve sozinho; juntos tornam a exploração cara.

- Ataque impedido: sobrescrever o endereço de retorno e desviar o
  programa.
- Laboratório: `labs/06-memoria`.

## 8. Segredo que sai do chip deixa de ser segredo

Chave que passa pela RAM pode ser lida da RAM. TPM, HSM, Secure Enclave,
YubiKey: a chave nasce, vive e morre dentro do chip; o que sai é a
assinatura, nunca a chave. É a diferença entre "guardei bem" e "não há
como copiar".

- Ataque impedido: malware com privilégio de administrador exportando a
  chave de disco ou de SSH.
- Onde ver: `labs/03-atestacao-tpm` (o TPM assina o *quote*; a chave não
  sai), `CHECKLIST.md` (chave SSH em token).

## 9. A cadeia de suprimentos é parte do sistema

A máquina passou por fábrica, transporte, revenda, instalação. Cada mão é
um ponto onde um chip, um firmware ou um cabo pode ter sido trocado. Não
dá para auditar tudo; dá para registrar o que chegou (inventário, hashes,
seriais) e comparar depois.

- Ataque impedido: trocar a máquina por uma igual com implante.
- Onde ver: `ferramentas/avaliar.py` guarda a foto da máquina para
  comparar com a próxima.

## 10. Falhe fechado, e diga que falhou

Quando a verificação não dá para ser feita (TPM ausente, assinatura
inválida, hash que não bate), o seguro é parar e avisar, não seguir
"em modo compatível". Um sistema que silencia a falha ensina quem o opera
a ignorar o aviso que importa.

- Ataque impedido: desligar a verificação e deixar tudo parecer normal.
- Onde ver: todo laboratório; o `avaliar.py` dá nota zero ao que não
  consegue medir, em vez de supor.
