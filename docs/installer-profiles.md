# Installer Profiles

TransportVault MVP uses explicit installer profiles to describe curated, supported boot/install media.

## Profile schema

Each profile in `profiles/*.yaml` must define:

- `name`: Human-readable display name shown in operator workflows.
- `type`: Media category (`installer`, `utility`, etc.).
- `path`: Vault path to the boot media ISO.
- `boot_mode`: Expected firmware mode (`uefi` for MVP profiles).
- `supported_versions`: List of versions validated for that media.
- `notes`: Operator-facing usage details and intent.
- `enabled`: Whether the profile is available for selection.

## Why explicit profiles in MVP

MVP **does not** provide generic "boot any ISO" compatibility. Instead, it supports a curated set of explicit profiles (RHEL, ESXi, and GParted) so boot entries, operator expectations, and audit events stay deterministic and supportable.
