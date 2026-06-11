# Drive Layout

This document describes the physical and logical layout of the TransportVault portable SSD, including partition definitions, the encrypted vault folder structure, and the access workflows for both Linux and Windows operators.

---

## Partition Table

The TransportVault drive uses a GPT (GUID Partition Table) with three partitions.

```text
┌─────────────────────────────────────────────────────────────┐
│  TransportVault SSD (GPT)                                   │
│                                                             │
│  Partition 1: EFI Boot Partition         ~1 GB              │
│  Partition 2: RHEL Rescue Environment    8–16 GB            │
│  Partition 3: Encrypted Vault            Remaining space    │
└─────────────────────────────────────────────────────────────┘
```

---

### Partition 1 — EFI Boot Partition

| Property    | Value                                |
|-------------|--------------------------------------|
| Filesystem  | FAT32                                |
| Size        | ~1 GB                                |
| Mount point | `/boot/efi` (when mounted on Linux)  |
| GPT type    | EFI System Partition (ESP)           |

**Purpose:**
Contains the GRUB2 bootloader and all boot-time assets required to start the TransportVault rescue environment and to chainload OS installer profiles. This partition is readable by UEFI firmware on any system without additional drivers.

**Contents:**
- `EFI/BOOT/BOOTX64.EFI` — UEFI boot entry
- `EFI/grub/grub.cfg` — GRUB menu configuration (`grub/grub.cfg`)
- GRUB modules and fonts
- ISO loop-mount helper scripts (`grub/scripts/`)

---

### Partition 2 — RHEL Rescue Environment

| Property    | Value                                       |
|-------------|---------------------------------------------|
| Filesystem  | XFS or ext4                                 |
| Size        | 8–16 GB                                     |
| Mount point | `/rescue` (when mounted from a running OS)  |

**Purpose:**
Houses a minimal, self-contained RHEL-based rescue operating system that boots independently of any target system. This partition provides all tooling needed for imaging, diagnostics, and auditing without relying on the target machine's OS.

**Key software included:**
- RHEL rescue OS (minimal install)
- Clonezilla and Partclone — disk imaging and cloning
- GParted — partition management
- `cryptsetup` / LUKS tools — vault unlock and management
- `sha256sum` / `sha512sum` — cryptographic verification
- TransportVault application (`transportvault/`) — main operator workflow
- Diagnostics and hardware audit tooling

**Security note:** This partition is **not encrypted**. It must not contain sensitive data, credentials, or vault key material. Its integrity is protected by the boot process; operators should verify the GRUB configuration is unchanged before use in high-assurance environments.

---

### Partition 3 — Encrypted Vault

| Property    | Value                                                    |
|-------------|----------------------------------------------------------|
| Filesystem  | LUKS2 container → ext4 or XFS inner filesystem           |
| Encryption  | AES-256-XTS (BitLocker for Windows MVP access)           |
| Size        | Remaining drive capacity (drive size minus partitions 1–2)|

**Purpose:**
Stores all sensitive operational data: golden images, installer ISOs, image manifests, audit logs, and deployment documentation. This is the only partition that holds sensitive or regulated data, and it **must remain encrypted at rest at all times**.

**Encryption approach:**
- **Primary (Linux):** LUKS2 with AES-256-XTS; passphrase-derived key via PBKDF2-SHA512
- **MVP Windows access:** BitLocker-encrypted data partition, accessible via Windows BitLocker Drive Encryption
- A dual-encryption or unlock-via-key-file strategy may be used to support both access paths simultaneously (see [Security Considerations](#security-considerations))

---

## Vault Folder Structure

When the encrypted vault partition is unlocked and mounted, the following directory hierarchy is used:

```text
<vault-mount>/
├── images/
│   ├── rhel/          — RHEL golden image files (.img, .partclone)
│   └── windows/       — Windows golden image files (.img, .partclone)
├── isos/
│   ├── rhel-kickstart.iso   — RHEL auto-installer ISO
│   ├── esxi-kickstart.iso   — VMware ESXi installer ISO
│   └── gparted.iso          — GParted Live ISO
├── logs/              — Structured audit log files (append-only)
├── manifests/         — SHA-256/SHA-512 image manifests (JSON)
└── docs/              — Deployment runbooks and field documentation
```

**Sensitive data is located exclusively in the encrypted vault (Partition 3).** No sensitive data should ever be written to Partition 1 (EFI) or Partition 2 (Rescue).

---

## Workflows

### Boot Workflow

```text
1. Operator inserts TransportVault drive and powers on (or reboots) the target system.
2. UEFI firmware detects the EFI System Partition (Partition 1) and loads GRUB.
3. GRUB presents the TransportVault boot menu:
      a. TransportVault Rescue Environment  ← boots Partition 2
      b. RHEL Auto Installer (Kickstart)
      c. ESXi Installer
      d. GParted Live
4. Operator selects an entry; GRUB loads the appropriate kernel/ISO.
5. For the Rescue Environment: RHEL boots from Partition 2 into the operator shell.
```

---

### Vault Workflow (Linux)

```text
1. Boot into the TransportVault Rescue Environment (Partition 2).
2. Run `vault/unlock.py` — operator provides the vault passphrase or key file.
3. LUKS2 decrypts Partition 3 and exposes a plaintext block device (e.g. /dev/mapper/vault).
4. Run `vault/mount.py` — mounts the decrypted device to the working directory.
5. Run `vault/inventory.py` — lists available images, ISOs, and manifests.
6. Perform desired operation:
      • Capture:  imaging/partclone.py → image written to images/ → hash verified → audit log updated
      • Restore:  manifest verified → imaging/restore.py → disk written → audit log updated
      • Installer profile: GRUB chainload → OS installer launched → audit log updated
7. When complete, unmount the vault and lock the LUKS container before removing the drive.
```

---

### Windows Access Workflow

```text
1. Insert the TransportVault drive into a Windows workstation.
2. Windows detects the BitLocker-encrypted partition (Partition 3).
3. Operator unlocks the vault using the BitLocker recovery key or passphrase via the
   Windows BitLocker Drive Encryption dialog (or `manage-bde` CLI).
4. Partition 3 mounts as a drive letter (e.g. D:\).
5. Operator can read/write vault contents using standard Windows Explorer or CLI tools.
6. To lock: use "Eject" or `manage-bde -lock <drive>:` before removing the drive.
```

**Note:** Windows will not recognize the EFI partition (FAT32, ESP type) or the RHEL Rescue partition as accessible drive letters. Only the BitLocker vault partition will appear.

---

### Linux Access Workflow (off-drive host)

```text
1. Insert the TransportVault drive into a Linux workstation (not booting from it).
2. Identify the vault partition:  lsblk -f  or  fdisk -l
3. Unlock the LUKS2 container:
      cryptsetup open /dev/<vault-partition> vault
      (enter passphrase when prompted)
4. Mount the unlocked device:
      mount /dev/mapper/vault /mnt/vault
5. Access vault contents under /mnt/vault/.
6. When finished:
      umount /mnt/vault
      cryptsetup close vault
```

---

## Security Considerations

| Topic | Detail |
|-------|--------|
| Sensitive data boundary | All sensitive data resides **only** in Partition 3 (Encrypted Vault). Partitions 1 and 2 must remain free of credentials, key material, and classified data. |
| Encryption algorithm | AES-256-XTS via LUKS2 (Linux); AES-256 via BitLocker (Windows). Both are FIPS-approved symmetric ciphers. |
| Key derivation | PBKDF2-SHA512 for LUKS2 passphrases. SHA-1 and MD5 are explicitly excluded per the FIPS-oriented design policy. |
| Key storage | No key material is stored on Partition 1 or Partition 2. Key files, if used, must be stored securely off-drive. |
| Physical security | The drive must be treated as a sensitive item. Loss of the drive exposes the encrypted vault to offline attack; strong, unique passphrases are required. |
| Boot integrity | The GRUB configuration and rescue OS on Partitions 1–2 are unencrypted. Operators in high-assurance environments should verify GRUB configuration integrity (e.g. hash check against a known-good manifest) before use. |
| Audit trail | All vault operations write structured, append-only audit log entries to `logs/` inside the encrypted vault. Logs are only accessible after vault unlock. |
| Dual-access (LUKS + BitLocker) | If a single physical partition must be accessible from both Linux (LUKS) and Windows (BitLocker), a supported dual-format or external unlock mechanism must be evaluated. The recommended MVP approach is a dedicated BitLocker-formatted vault for Windows use cases; LUKS is the primary Linux format. |

---

## Related Documents

- [Architecture](architecture.md) — Overall system architecture and data flow
- [FIPS Strategy](fips-strategy.md) — Cryptographic design rationale
- [Auditing](auditing.md) — Audit log format and chain-of-custody design
- [README](../README.md) — Project overview and MVP workflow summary
