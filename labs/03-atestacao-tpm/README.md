# 03. Atestação (TPM)

```bash
python3 tpm.py
```

Três coisas para ver no código:

- `extend` é o único jeito de mudar um PCR, e ele é uma via de mão única.
- O *quote* leva um `nonce` do verificador: sem ele, um quote antigo de
  uma máquina íntegra serviria para sempre (replay).
- A chave que assina o quote está dentro do objeto `TPM` e nunca é
  exportada: o verificador só tem a pública.

Com hardware de verdade (Linux com TPM 2.0 e `tpm2-tools`):

```bash
sudo tpm2_pcrread sha256:0,7
```

Anote os valores, atualize a BIOS, leia de novo: o PCR 0 muda, o 7
(estado do Secure Boot) não. É a mesma coisa que `boot_medido` faz.
