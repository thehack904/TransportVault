# TransportVault

**Portable deployment and recovery platform for secure, auditable, air-gapped environments.**

---

## What Is TransportVault?

TransportVault is a self-contained, bootable deployment and imaging toolkit designed for use in air-gapped, classified, or infrastructure-restricted environments. It is carried on a portable encrypted drive and provides everything needed to:

- Capture and restore golden images of Windows and RHEL systems
- Launch curated installer profiles (RHEL, ESXi, GParted) directly from the drive
- Verify image integrity using cryptographic hashes
- Record tamper-evident audit logs for every operation

TransportVault is built with a FIPS 140-oriented design philosophy. It does not claim formal FIPS 140 certification, but all cryptographic operations are designed to use only FIPS-approved algorithms (AES-256, SHA-256, SHA-512) and constructs, ensuring alignment with government and defense security standards.

---

## Project Goals

- Provide a reliable, portable platform for bare-metal imaging and OS deployment in disconnected environments
- Ensure all deployment actions are cryptographically auditable and reproducible
- Support common field use cases: golden image deployment, disk cloning, OS installation, and system recovery
- Minimize dependency on external infrastructure (no network required, no cloud dependency)
- Apply defense-in-depth principles: encrypted vault storage, verified payloads, and signed audit records

---

## MVP — Minimum Viable Product

The MVP validates the complete end-to-end workflow on a portable encrypted drive:

| Step | Description |
|------|-------------|
| Boot | System boots from TransportVault drive into a controlled Linux environment |
| Unlock / Mount Vault | Encrypted vault partition is unlocked and mounted (LUKS) |
| List Available Images | Operator reviews available golden images in the vault inventory |
| Capture Image | Source disk or partition is captured using partclone / Clonezilla wrappers |
| Verify Image | SHA-256 hash is computed and verified against the stored manifest |
| Restore Image | A stored image is restored to a target disk |
| Launch Installer Profile | A supported installer (RHEL, ESXi, GParted) is launched via GRUB |
| Write Audit Records | All operations are written to a structured, append-only audit log |
| Review Logs | Operator can review the audit trail before removing the drive |

### MVP Scope

The MVP (Minimum Viable Product) is focused on proving these core capabilities:

- **RHEL Golden Image deployment**
- **Windows Golden Image deployment**
- **Image capture**
- **Image restore**
- **Encrypted vault storage**
- **Windows and Linux vault accessibility**
- **RHEL, ESXi, and GParted installer profiles**
- **Audit logging and verification**

### MVP Workflow — RHEL Golden Image

1. Boot the target system from the TransportVault drive
2. Unlock the vault partition (`vault/unlock.py`)
3. Mount the vault to the working directory (`vault/mount.py`)
4. List available images in the vault (`vault/inventory.py`)
5. Capture the RHEL partition to the vault using the partclone wrapper (`imaging/partclone.py`)
6. Verify the captured image against its SHA-256 manifest (`crypto/verification.py`)
7. Write the capture event to the audit log (`audit/logger.py`)
8. To restore: mount vault, select image, run restore (`imaging/restore.py`), verify, and log

### MVP Workflow — Windows Golden Image

1. Boot from the TransportVault drive (Windows partition must be offline)
2. Unlock and mount the vault
3. List available images
4. Capture the Windows partition using the partclone wrapper
5. Verify the captured image against its SHA-256 manifest
6. Write audit records
7. To restore: mount vault, select image, run restore, verify, and log

### MVP Workflow — GParted Profile

1. Boot from the TransportVault drive
2. Select the **GParted Live** entry in the GRUB menu (`grub/grub.cfg`)
3. Use GParted interactively for disk partitioning or inspection
4. Audit entry is written on profile launch

### MVP Workflow — ESXi Profile

1. Place VMware ESXi ISO on the vault partition
2. Boot from the TransportVault drive
3. Select the **ESXi Installer** entry in the GRUB menu
4. Complete the ESXi installation using the standard VMware wizard
5. Audit entry is written on profile launch
6. *Note: ESXi media must be sourced and placed manually; TransportVault provides the launch mechanism only*

---

## Non-Goals

The following are explicitly out of scope for the MVP:

- General-purpose commercial backup suite feature parity
- Generic boot-any-ISO compatibility
- Unvalidated installer media support
- Cloud backup
- Incremental backup
- Enterprise management console
- Formal FIPS certification claims (initial compliance goal is FIPS 140-oriented architecture, not certification)

---

## High-Level Architecture

```
TransportVault Drive (USB / SSD)
├── GRUB Bootloader (grub/grub.cfg)
│   ├── TransportVault OS Environment
│   ├── RHEL Auto Installer (profiles/rhel-installer.yaml)
│   ├── ESXi Installer (profiles/esxi-installer.yaml)
│   └── GParted Live (profiles/gparted.yaml)
│
├── Encrypted Vault Partition (LUKS / AES-256)
│   ├── Golden Images (captured partitions)
│   ├── Image Manifests (SHA-256 checksums)
│   └── Audit Logs (append-only structured records)
│
└── TransportVault Application (transportvault/)
    ├── vault/          — Unlock, mount, inventory
    ├── imaging/        — Capture, restore (partclone, Clonezilla)
    ├── crypto/         — SHA-256 hashing and verification
    ├── audit/          — Structured logging and reports
    ├── hardware/       — Disk detection and hardware inventory
    ├── ui/             — Terminal menus and workflow screens
    └── config.py       — Runtime configuration
```

### Data Flow

```
Operator boots drive
       │
       ▼
Vault unlock (LUKS passphrase or key file)
       │
       ▼
Vault mount → Image inventory presented
       │
       ├─► Capture workflow:  disk → partclone → image file → SHA-256 hash → manifest → audit log
       ├─► Restore workflow:  manifest → verify hash → partclone restore → audit log
       └─► Installer profile: GRUB chainload → OS installer → audit log
```

---

## FIPS 140-Oriented Design Philosophy

TransportVault is designed with alignment to FIPS 140-2 and FIPS 140-3 principles. **It does not claim or hold formal FIPS certification.**

| Design Area | Approach |
|-------------|----------|
| Vault encryption | AES-256-XTS (LUKS2) — FIPS-approved symmetric cipher |
| Image verification | SHA-256 / SHA-512 checksums — FIPS-approved hash algorithms |
| Audit integrity | Append-only logs; hash chaining planned for future releases |
| Key handling | Passphrase-derived keys via PBKDF2-SHA512; key files stored only on drive |
| Algorithm selection | Only FIPS-approved algorithms used; MD5 and SHA-1 are explicitly excluded |
| Dependency posture | Minimal external libraries; cryptographic operations use system-level primitives |

The intent is that an operator working in a FIPS-required environment can audit the algorithm choices and satisfy their local security officer, even in the absence of a third-party FIPS certificate for TransportVault itself.

---

## Future Roadmap Summary

The following capabilities are planned for post-MVP releases. See [ROADMAP.md](ROADMAP.md) for details.

| Phase | Capability |
|-------|------------|
| v1.1 | Hash-chained audit log (tamper-evident chain of custody) |
| v1.2 | Windows installer profile (WinPE-based) |
| v1.2 | Automated hardware inventory report on boot |
| v1.3 | Signed image manifests (GPG or X.509) |
| v1.3 | Multi-partition / full-disk capture workflows |
| v2.0 | Graphical terminal UI (TUI) for operator workflow |
| v2.0 | TPM 2.0 key sealing for vault unlock |
| v2.1 | Automated RHEL Kickstart profile generation |
| Future | Formal FIPS 140-3 evaluation pathway (if funded) |

---

## Known Limitations (v1.0 MVP)

- ESXi profile requires the operator to supply the ESXi ISO; it is not bundled
- Windows capture requires the Windows partition to be offline at capture time
- Audit logs are plain structured text in v1.0; tamper-evident chaining is a v1.1 feature
- No graphical interface; all workflows are terminal-driven
- GRUB configuration must be updated manually when adding new installer profiles
- FIPS alignment is by design intent only; no third-party certification is held

---

## Repository Structure

```
TransportVault/
├── README.md                  — This document
├── CHANGELOG.md               — Version history
├── ROADMAP.md                 — Planned features
├── SECURITY.md                — Security policy and reporting
├── docs/
│   ├── architecture.md        — Detailed architecture documentation
│   ├── auditing.md            — Audit log format and chain-of-custody design
│   ├── drive-layout.md        — Physical and logical drive layout
│   ├── installer-profiles.md  — Installer profile schema and MVP scope
│   └── fips-strategy.md       — FIPS 140-oriented design rationale
├── grub/
│   ├── grub.cfg               — GRUB bootloader configuration
│   └── scripts/               — GRUB helper scripts
├── manifests/
│   └── manifest-schema.json   — JSON schema for image manifests
├── profiles/
│   ├── rhel-installer.yaml    — RHEL auto-installer profile
│   ├── esxi-installer.yaml    — ESXi installer profile
│   └── gparted.yaml           — GParted Live profile
├── samples/
│   └── sample-manifest.json   — Example image manifest
├── tests/
│   └── test_manifest.py       — Manifest validation tests
└── transportvault/
    ├── main.py                — Entry point
    ├── config.py              — Runtime configuration
    ├── audit/                 — Audit logging and reporting
    ├── crypto/                — Hashing and verification
    ├── hardware/              — Disk and hardware detection
    ├── imaging/               — Image capture and restore
    ├── ui/                    — Terminal UI and menus
    └── vault/                 — Vault unlock, mount, and inventory
```

---

## License

See repository for license details.
