# Checklist de endurecimento de uma máquina

Para uma estação ou servidor Linux. Cada item tem o **comando que prova**:
sem a prova, o item não está feito. `ferramentas/avaliar.py` roda os
itens marcados com ⚙ sozinho e dá a nota.

## Antes de ligar

- [ ] **Inventário**: modelo, serial, versão de BIOS/UEFI, lista de
  dispositivos PCI e USB, guardados fora da máquina. ⚙
  `sudo dmidecode -t system,bios | grep -E "Serial|Version"`; `lspci`; `lsusb`
- [ ] **Senha no setup (BIOS/UEFI)** e ordem de boot travada no disco
  interno. Prova: tentar entrar no setup sem senha.
- [ ] **Secure Boot ligado**. ⚙
  `mokutil --sb-state` ou `od -An -t u1 /sys/firmware/efi/efivars/SecureBoot-*`
  (último byte 1 = ligado)
- [ ] **TPM 2.0 presente e ativo**. ⚙
  `ls /dev/tpm0 /dev/tpmrm0`; `cat /sys/class/tpm/tpm0/tpm_version_major`
- [ ] **Detecção de abertura de gabinete** (chassis intrusion), se o
  hardware tiver.

## Disco e memória

- [ ] **Disco cifrado** (LUKS2 ou equivalente), com a chave selada no TPM
  ou com senha forte na inicialização. ⚙
  `lsblk -o NAME,TYPE,FSTYPE,MOUNTPOINT | grep crypt`
- [ ] **IOMMU ligada** para que um dispositivo PCIe/Thunderbolt não leia a
  RAM inteira por DMA. ⚙
  `cat /proc/cmdline | grep -E "intel_iommu=on|amd_iommu=on"`;
  `ls /sys/kernel/iommu_groups | wc -l` (maior que zero)
- [ ] **Thunderbolt com autorização de dispositivo** (`boltctl list`), ou
  desligado no setup se não for usado.
- [ ] **Hibernação desligada** ou com swap cifrado: a imagem de hibernação
  é a RAM inteira em disco.

## Portas e periféricos

- [ ] **Inventário de USB em uso** e alerta para dispositivo novo de
  interface humana (teclado, mouse) que aparece sozinho: é a assinatura do
  BadUSB. ⚙ `labs/04-inventario-usb`
- [ ] **USBGuard** ou regra udev bloqueando HID não autorizado
  (`labs/04-inventario-usb/99-bloquear-hid-desconhecido.rules`).
- [ ] **Portas físicas não usadas desligadas** no setup (USB traseiras,
  serial, PS/2, FireWire).

## Firmware

- [ ] **BIOS/UEFI na versão atual do fabricante**, com data registrada.
  `sudo dmidecode -s bios-version; sudo dmidecode -s bios-release-date`
- [ ] **fwupd** para o que ele cobre (controladoras, teclados, docks):
  `fwupdmgr get-devices; fwupdmgr get-updates`
- [ ] **Manifesto do `/boot`** gerado e guardado fora da máquina;
  verificado depois de cada atualização. ⚙ `labs/05-integridade-firmware`

## Sistema

- [ ] **Kernel com lockdown** quando o Secure Boot está ligado:
  `cat /sys/kernel/security/lockdown`
- [ ] **ASLR ligado**: `cat /proc/sys/kernel/randomize_va_space` (2). ⚙
- [ ] **Chave SSH em token de hardware** (YubiKey, `ssh-keygen -t ed25519-sk`),
  não em arquivo.
- [ ] **Atualizações automáticas de segurança** ligadas e registradas.

## Prova de vida, uma vez por mês

- [ ] Rodar `python3 ferramentas/avaliar.py --salvar` e comparar com o mês
  anterior. Item que mudou sem você saber é incidente, não detalhe.
