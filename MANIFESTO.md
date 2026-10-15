<div align="center">

# Manifesto: segurança é verificação

</div>

> **Uma afirmação, muitas instâncias.** Este documento tira a segurança de hardware
> do plano físico (TPM, UEFI, USB) e a reescreve como um caso particular de uma ideia
> mais geral — a mesma do [`james-theorems`](https://github.com/thiagopatzdorf/james-theorems).
> Cada afirmação abaixo está classificada na [§5](#5-tabela-de-honestidade) como
> **teorema**, **correspondência**, **modelo** ou **hipótese**.

---

## 1. A pergunta

Segurança não é uma lista de ameaças. É uma pergunta:

> **Quando é racional confiar numa máquina?**

A resposta deste repositório tem uma forma só: confiar é racional quando a confiança
pode ser **verificada** a partir de uma **raiz** que não se pode alterar. Tudo o mais
— assinatura, atestação, canário, cifra — é engenharia dessa frase.

## 2. Por que verificar é o centro

Há uma assimetria física entre **gerar** uma garantia e **conferi-la**. Assinar uma
imagem exige a chave privada e tempo; conferir a assinatura exige só a chave pública
e microssegundos. Queimar um *fuse* é irreversível e caro; ler o *fuse* é trivial.
Medir o boot num TPM custa o boot inteiro; comparar o PCR com uma política é um `memcmp`.

Essa assimetria é a mesma que organiza o `james-theorems`: **descobrir é caro,
verificar é barato.** Lá ela é provada como o teorema `amortizacao` — começando de uma
base vazia, o custo total é `D·descoberta + N·verificação`, e quando o número `D` de
coisas distintas a provar cresce mais devagar que o número `N` de decisões, o custo por
decisão tende ao de verificar. Em segurança de hardware, `D` é o número de raízes que
você precisa provar (uma chave de fábrica, um *fuse*, uma política de PCR) e `N` é o
número de inicializações, pacotes, imagens. `D` é minúsculo; `N` é a vida da máquina.
**É por isso que a defesa escala e o ataque, não.**

## 3. As três raízes

Toda tecnologia de segurança de hardware é uma destas três coisas, ou a combinação delas:

1. **Raiz de confiança** — algo que não se pode alterar, de onde a verificação parte.
   Uma ROM, um *fuse*, uma chave em silício. Sem ela, não há o que verificar: quem
   verifica poderia estar comprometido. (Cadeia de boot, Secure Boot.)
2. **Propagação por verificação** — cada estágio prova o próximo a partir da raiz, por
   assinatura (impedir) ou por medição (registrar). A confiança caminha sem nunca ser
   assumida. (TPM, atestação remota, dm-verity.)
3. **Confinamento do que não se pode verificar** — o que fica fora da cadeia (uma porta
   física, uma RAM lida por DMA, um segredo que saiu do chip) é reduzido ou isolado, não
   confiado. (IOMMU, cifra de disco, HSM, enclave.)

Os seis laboratórios são instâncias dessas três. Nenhum é um assunto novo; são a mesma
frase em escalas diferentes.

## 4. O limite honesto

Verificação tem fronteira, e nomeá-la é parte da honestidade:

- **A raiz não se verifica a si mesma.** Em algum ponto você confia na fábrica, no
  silício, na cadeia de suprimentos. Segurança não elimina a confiança; ela a **empurra
  para o menor conjunto possível** e a torna explícita.
- **Verificar não é impedir.** Medir o boot (TPM) diz o que rodou; não impede que rode.
  Impedir (Secure Boot) e medir (atestação) são defesas diferentes e se completam.
- **O que não se pode medir não vira confiança.** Falhar fechado — parar e avisar quando
  a verificação não é possível — é a regra, não a exceção. Um sistema que silencia a
  falha ensina a ignorar o aviso que importa.

## 5. Tabela de honestidade

| afirmação | tipo | onde |
|---|---|---|
| custo total = `D·descoberta + N·verificação`, de base vazia | **teorema** (provado em Lean) | [`james-theorems`](https://github.com/thiagopatzdorf/james-theorems), `amortizacao` |
| segurança de hardware é esse mesmo modelo, com `D` = raízes e `N` = decisões | **correspondência** | §2 deste manifesto |
| as três raízes esgotam as tecnologias de segurança de hardware | **modelo** | §3 |
| o custo real de operar cai quando a cadeia de confiança encurta a superfície | **hipótese** (a medir) | `ferramentas/avaliar.py` mede uma máquina; a tendência, não |

## 6. O que fazer com isto

Ler os [princípios](PRINCIPIOS.md), rodar os [laboratórios](labs), medir a sua máquina
com o [avaliador](ferramentas/avaliar.py), e — a parte que fecha o ciclo — pegar uma
máquina de verdade, aplicar o [checklist](CHECKLIST.md), e **medir antes e depois**.
Conhecimento caro (entender) virando verificação barata (um comando que confere). É o
ofício.
