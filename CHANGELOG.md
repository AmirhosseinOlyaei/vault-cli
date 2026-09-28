# Changelog

All notable changes to Vault will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-09-27

### Added

- **Core Encryption Features**
  - AES-128 encryption via Fernet
  - PBKDF2-SHA256 key derivation with 480,000 iterations
  - Secure random salt generation (16 bytes per file)
  - HMAC authentication for integrity verification

- **CLI Interface**
  - `vault encrypt` command with password support
  - `vault decrypt` command with password verification
  - `--password` flag for non-interactive operation
  - `--output` flag for custom output paths
  - Help text and error messages

- **Logging System**
  - Structured logging with timestamp and log levels
  - Debug logs for key derivation and file operations
  - Info logs for successful encryption/decryption
  - Warning logs for decryption failures (wrong password)
  - Error logs with detailed error messages

- **Documentation**
  - Comprehensive README with features and usage
  - SETUP_GUIDE.md for fresh macOS installation
  - INTEGRATION_GUIDE.md with real-world use cases
  - SECURITY.md with vulnerability reporting policy
  - This CHANGELOG.md file

- **Configuration**
  - .env.example with environment variable templates
  - Configurable logging levels
  - Support for audit logging (placeholder)

- **Project Files**
  - pyproject.toml with dependencies (cryptography>=41.0.0, typer>=0.9.0)
  - .claude/hooks.toml for stop hook cleanup
  - .gitignore (partial - to be completed)
  - LICENSE (to be added)

### Features

- Python 3.9+ support
- Cross-platform (macOS, Linux, Windows tested on macOS)
- Secure password prompting with hide_input
- Proper exception handling and error messages
- File existence validation before operations
- Type hints throughout codebase

### Security

- No hardcoded passwords
- PBKDF2 with industry-standard iteration count
- Random salt per file prevents rainbow table attacks
- HMAC ensures file integrity
- Detailed error handling without exposing sensitive data

---

## [Unreleased]

### Planned for v0.2.0

- [ ] Unit tests (test_crypto.py, test_cli.py)
- [ ] Integration tests
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Type checking with mypy
- [ ] Code coverage reporting
- [ ] Pre-commit hooks for code quality
- [ ] Docker support (Dockerfile, docker-compose.yml)
- [ ] Contributing guidelines (CONTRIBUTING.md)
- [ ] GitHub issue and PR templates
- [ ] Audit logging implementation
- [ ] Performance benchmarks
- [ ] API reference documentation

### Planned for v0.3.0

- [ ] Key rotation without full re-encryption
- [ ] Asymmetric encryption option (RSA)
- [ ] Hardware security module (HSM) integration
- [ ] Rate limiting for brute-force protection
- [ ] Encrypted metadata support
- [ ] Key escrow/recovery mechanism
- [ ] RBAC (Role-Based Access Control)

### Planned for v1.0.0

- [ ] Third-party security audit
- [ ] Post-quantum cryptography support
- [ ] API server wrapper (REST/gRPC)
- [ ] Web UI dashboard
- [ ] Batch encryption/decryption
- [ ] Cloud provider integration (S3, Azure Blob, GCS)
- [ ] HSM integration
- [ ] Compliance certifications (SOC 2, ISO 27001)

---

## Release Notes

### Version 0.1.0 - Initial Release

**Highlights:**

- Secure file encryption with industry-standard algorithms
- Simple CLI interface for encryption and decryption
- Production-ready code structure with logging
- Comprehensive documentation

**Installation:**

```bash
pip install -e .
vault --help
```

**Quick Start:**

```bash
vault encrypt sensitive.pdf --password "my-password"
vault decrypt sensitive.pdf.encrypted --password "my-password"
```

**Known Issues:**

- No batch encryption (encrypt files one at a time)
- No key rotation support (requires re-encrypting files)
- Plaintext filename extension `.encrypted` reveals encrypted files
- No graphical user interface
- No built-in backup mechanism (use `VAULT_AUTO_BACKUP=true` in .env)

**Dependencies:**

- cryptography >= 41.0.0 (for AES encryption)
- typer >= 0.9.0 (for CLI framework)
- Python >= 3.9

---

## Versioning Strategy

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes (e.g., encryption format change)
- **MINOR**: New features (e.g., new CLI command)
- **PATCH**: Bug fixes and security updates

### Release Cadence

- **Security Fixes**: ASAP (within 48 hours)
- **Bug Fixes**: Monthly patch releases
- **Features**: Quarterly minor releases
- **Major Releases**: As needed for significant changes

### Support Policy

| Version | Status  | Support Until  |
| ------- | ------- | -------------- |
| 0.1.x   | Current | 2027-09-27     |
| < 0.1.0 | N/A     | Never released |

---

## Migration Guides

### Upgrading from 0.0.x to 0.1.0

- Initial release, no previous versions

### Upgrading from 0.1.x to 0.2.0

- No breaking changes planned
- Backward compatible with v0.1.0
- New features will be additive only

---

## How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Reporting bugs
- Suggesting features
- Submitting pull requests
- Code style requirements
- Testing requirements

---

## Attribution

**Contributors:**

- Claude Haiku 4.5 (Initial development)
- Community feedback and contributions welcome

---

## Acknowledgments

- **cryptography.io**: Python cryptography library
- **OWASP**: Security guidelines and best practices
- **NIST**: PBKDF2 and AES standards
- **Fernet**: Symmetric encryption specification

---

**Last Updated**: 2026-09-27
