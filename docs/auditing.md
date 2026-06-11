# Auditing

TransportVault writes a structured, append-only audit log for every significant operator action. The log is intended to support tamper-evident chain-of-custody reporting and satisfy security requirements in air-gapped and classified environments.

---

## Audit Log Format

Each record is a single-line JSON object (JSON Lines / NDJSON). One event per line. Records are appended in chronological order and must never be edited or deleted.

### Example Record

```json
{"timestamp":"2026-06-11T18:05:00Z","event_type":"VAULT_UNLOCK","actor":"operator-01","hostname":"field-deploy-01","operation_id":"a1b2c3d4-0001-0001-0001-000000000001","image_name":null,"source_disk":null,"target_disk":null,"result":"success","details":{"method":"passphrase"},"previous_event_hash":null,"chain_of_custody":{"chain_version":"v1","entry_hash":"1ad2f1f0...","record_signature":null,"signing_key_id":null}}
```

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string (ISO 8601 UTC) | When the event occurred, e.g. `2026-06-11T18:05:00Z` |
| `event_type` | string (enum) | Identifies the operation; see [Event Types](#event-types) below |
| `actor` | string | Operator identity or service account that triggered the action |
| `hostname` | string | Hostname of the system running TransportVault |
| `operation_id` | string (UUID v4) | Unique identifier grouping related start/complete events |
| `image_name` | string \| null | Name of the image involved, or `null` if not applicable |
| `source_disk` | string \| null | Source disk device (e.g. `/dev/nvme0n1`), or `null` |
| `target_disk` | string \| null | Target disk device (e.g. `/dev/sda`), or `null` |
| `result` | string (enum) | Outcome: `started`, `success`, `failure` |
| `details` | object | Free-form key/value pairs providing operation-specific context |
| `previous_event_hash` | string \| null | SHA-256 digest of the immediately preceding log record (raw UTF-8 line), enabling hash-chained verification; `null` for the first record in the log |
| `chain_of_custody` | object | Reserved chain metadata for future signed chain-of-custody support; see [Future Chain-of-Custody Fields](#future-chain-of-custody-fields) |

---

## Event Types

| Event Type | Description |
|------------|-------------|
| `VAULT_UNLOCK` | The encrypted vault partition was successfully unlocked |
| `VAULT_LOCK` | The vault partition was locked and unmounted |
| `IMAGE_CAPTURE_STARTED` | A disk or partition capture operation began |
| `IMAGE_CAPTURE_COMPLETED` | A capture operation finished (success or failure) |
| `IMAGE_RESTORE_STARTED` | A restore operation targeting a disk began |
| `IMAGE_RESTORE_COMPLETED` | A restore operation finished (success or failure) |
| `IMAGE_VERIFY_STARTED` | SHA-256 integrity verification of an image began |
| `IMAGE_VERIFY_COMPLETED` | Integrity verification finished (success or failure) |
| `INSTALLER_BOOT_SELECTED` | An installer profile (RHEL, ESXi, GParted, etc.) was selected and booted via GRUB |
| `HARDWARE_INVENTORY_COLLECTED` | A hardware inventory snapshot was recorded |
| `ADMIN_CHANGE` | A privileged configuration change was made (e.g. adding a key file, modifying vault settings) |

---

## `result` Values

| Value | Meaning |
|-------|---------|
| `started` | The operation has begun; a corresponding `_COMPLETED` event is expected |
| `success` | The operation completed successfully |
| `failure` | The operation failed; `details` should include an `error` key with a description |

---

## `details` Object

The `details` field is a free-form JSON object. Common keys used across event types:

| Key | Used By | Description |
|-----|---------|-------------|
| `method` | `VAULT_UNLOCK` | Unlock mechanism: `passphrase` or `key_file` |
| `image_path` | Capture / Restore / Verify | Vault-relative path to the image file |
| `hash_algorithm` | Capture / Verify | Hash algorithm used, e.g. `sha256` |
| `sha256` | Capture / Verify | Computed or expected SHA-256 digest |
| `bytes_written` | Capture / Restore | Total bytes written during the operation |
| `profile` | `INSTALLER_BOOT_SELECTED` | Profile name selected (e.g. `rhel-installer`, `esxi-installer`, `gparted`) |
| `inventory` | `HARDWARE_INVENTORY_COLLECTED` | Structured hardware inventory snapshot |
| `change_description` | `ADMIN_CHANGE` | Human-readable description of the change |
| `error` | Any `failure` result | Error message or exception summary |

---

## Chain-of-Custody Design

The `previous_event_hash` field links each record to the one before it, forming a hash chain across the entire log file. This makes undetected tampering — inserting, removing, or modifying a record — computationally infeasible.

### How the chain is built

1. The first record written to a new log file sets `previous_event_hash` to `null`.
2. Before appending a new record, TransportVault computes the SHA-256 digest of the **raw UTF-8 bytes** of the last line in the log file (the line as it appears on disk, including the trailing newline).
3. That digest is placed in the new record's `previous_event_hash` field.
4. The new record is appended to the log.

### Verifying the chain

A verifier reads the log line by line and, for each record after the first, confirms that `previous_event_hash` equals the SHA-256 digest of the preceding raw line. Any mismatch indicates tampering.

> **Note:** Hash chaining is an architectural feature of v0.1 audit records. The `audit/reports.py` module will provide automated chain verification in a future release (see ROADMAP.md v1.1).

## Future Chain-of-Custody Fields

To support a future signed chain-of-custody implementation without breaking the schema, each event includes a `chain_of_custody` object with the following keys:

| Key | Type | Description |
|-----|------|-------------|
| `chain_version` | string | Chain format version (`v1` for MVP records) |
| `entry_hash` | string | SHA-256 digest of the current canonical JSON record |
| `record_signature` | string \| null | Detached signature for `entry_hash`; `null` until signing is enabled |
| `signing_key_id` | string \| null | Identifier for the signing key/certificate used for `record_signature` |

MVP records may set `record_signature` and `signing_key_id` to `null`, but the object and keys are present so future releases can enable signatures and external custody attestations with no breaking schema changes.

---

## Log File Location

The audit log is stored inside the encrypted vault partition:

```
<vault_mount_point>/audit/transportvault-audit.log
```

The log file is append-only. Operators must not edit or rotate this file. Log archival and export procedures are defined in the operational runbook.

---

## Sample Log File

See [`samples/sample-audit.log`](../samples/sample-audit.log) for a realistic example covering a full operator session including vault unlock, image capture, image verification, image restore, and vault lock.
