# FIPS 140-Oriented Strategy (MVP)

## Purpose

This document defines TransportVault's **FIPS 140-oriented architecture direction** for the MVP.

TransportVault is being built to support operations in environments that require strong cryptographic controls and auditability. The MVP goal is alignment-by-design with FIPS expectations, not formal certification claims.

## Positioning: What We Are (and Are Not) Claiming

### 1) FIPS-oriented architecture

TransportVault uses a design approach that prioritizes:

- FIPS-approved cryptographic algorithms (for example AES-256 and SHA-256)
- controlled cryptographic usage patterns
- operational auditability
- documented and repeatable procedures

This is an **architecture and implementation direction**.

### 2) Operating in FIPS mode

For the MVP, the target operational model is a rescue OS that can run in **FIPS mode** where required by mission policy.

Operating in FIPS mode depends on the configured runtime environment (OS settings, crypto libraries, boot configuration, and operational controls), not only on application code.

### 3) Formal FIPS validation

TransportVault does **not** claim formal FIPS 140-2 or FIPS 140-3 validation for the MVP.

Formal validation requires accredited laboratory testing and certification workflows outside this repository's current MVP scope.

## MVP Compliance Assumptions and Initial Design Direction

The MVP assumes deployment in controlled environments where administrators can enforce OS hardening and crypto policy.

### Rescue environment and platform assumptions

- RHEL-based rescue environment
- FIPS mode target for rescue OS
- controlled package and configuration baseline for reproducible behavior

### Cryptographic and data protection assumptions

- approved cryptographic algorithm selection only
- encrypted vault storage for protected image/media content
- SHA-256 verification for image and payload integrity checks

### Operational control assumptions

- auditable operations for capture, restore, verify, and installer-launch workflows
- documented procedures for operator usage, vault handling, and verification steps

## Guardrails on Compliance Language

The MVP may describe:

- FIPS-oriented design decisions
- FIPS-mode operational targets
- algorithm and control choices intended to support regulated environments

The MVP must not describe:

- formal FIPS certification status for TransportVault
- unsupported claims of compliance attestation
- completed third-party validation that has not occurred

## Future Compliance Growth Areas

Post-MVP roadmap and evidence-development areas include:

- NIST 800-171 alignment mapping for applicable security requirements
- RMF support documentation packages and control-trace artifacts
- STIG hardening baselines for rescue environment and operational profiles
- Secure Boot validation procedures and documentation
- chain-of-custody reporting improvements for media handling and audit timelines
- compliance evidence collection workflows (configuration snapshots, logs, manifests, and review records)

These are planned maturity steps and should be treated as forward-looking capabilities, not current certifications.
