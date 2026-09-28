# Security Policy

## Reporting Security Vulnerabilities

**DO NOT** open a public GitHub issue for security vulnerabilities. Instead, please report security issues responsibly.

### How to Report

1. **Email**: Send details to `security@[your-domain].com` (update this)
2. **GitHub Security Advisory**: Use GitHub's [Report a vulnerability](https://github.com/AmirhosseinOlyaei/vault-cli/security/advisories/new) feature
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

We take all security reports seriously and will respond within 48 hours.

---

## Security Considerations

### What Vault Protects

✅ **File Confidentiality**: Files are encrypted with AES-128 via Fernet
✅ **Data Integrity**: HMAC ensures files haven't been tampered with
✅ **Key Derivation**: PBKDF2-SHA256 with 480,000 iterations resists brute-force attacks
✅ **Unique Salts**: Every encrypted file has a unique 16-byte salt

### What Vault Does NOT Protect

❌ **Metadata**: Filename, file size, and timestamp are NOT encrypted
❌ **Digital Signatures**: Cannot verify who encrypted a file
❌ **Key Management**: You are responsible for password strength and safekeeping
❌ **Access Control**: Once decrypted, plaintext is unprotected
❌ **Side-Channel Attacks**: No protection against timing or power analysis attacks

---

## Security Best Practices

### Password Security

1. **Use Strong Passwords**
   - Minimum 16 characters
   - Mix uppercase, lowercase, numbers, and symbols
   - Avoid dictionary words and personal information
   - Example: `Tr0pic@lThunder#2024!Secure`

2. **Never Reuse Passwords**
   - Use unique passwords for different data types
   - Rotate passwords quarterly
   - Use a password manager (1Password, Bitwarden, etc.)

3. **Protect Your Master Password**
   - Don't share it via email, Slack, or chat
   - Store it securely (password manager, HSM)
   - Never hardcode in applications or scripts

### File Management

1. **Secure Deletion**

   ```bash
   # After encrypting, securely delete the original
   shred -vfz -n 3 sensitive_file.txt
   # Or use srm on macOS
   srm sensitive_file.txt
   ```

2. **Backup Encrypted Files**
   - Store encrypted backups in multiple locations
   - Use encrypted cloud storage (S3 with encryption, Azure Blob, etc.)
   - Verify backup decryption periodically

3. **Clean Temporary Files**
   - Enable `VAULT_AUTO_BACKUP=true` to backup before encryption
   - Use stop hooks to clean `__pycache__` and temp files
   - Monitor for accidentally created plaintext copies

### Operational Security

1. **Environment Variables**

   ```bash
   # Load from secure sources, not hardcoded
   export VAULT_PASSWORD=$(aws secretsmanager get-secret-value --secret-id vault-password --query SecretString --output text)
   vault decrypt file.encrypted --password "$VAULT_PASSWORD"
   ```

2. **Access Control**
   - Restrict file permissions to owner only: `chmod 600 file.encrypted`
   - Use directory permissions: `chmod 700 encrypted_dir/`
   - Audit who has access to encryption keys

3. **Monitoring & Logging**
   - Enable `VAULT_AUDIT_LOG=true` to track operations
   - Review logs regularly for unauthorized access
   - Alert on repeated failed decryption attempts
   - Monitor for unusual encryption/decryption patterns

---

## Cryptographic Details

### Encryption Algorithm: Fernet (AES-128-CBC)

```
├── Key Derivation
│   ├── Algorithm: PBKDF2-SHA256
│   ├── Iterations: 480,000
│   ├── Salt: 16 random bytes
│   └── Output: 256-bit key
│
├── Encryption
│   ├── Algorithm: AES-128-CBC
│   ├── Key Size: 128 bits
│   └── IV: Random (included in ciphertext)
│
└── Authentication
    ├── Algorithm: HMAC-SHA256
    └── Verifies: Ciphertext integrity & authenticity
```

### File Format

```
[Salt (16 bytes)][Fernet Token]
                 └─[IV (16 bytes)][Ciphertext][HMAC (32 bytes)]
```

### Key Derivation

```
Key = PBKDF2-SHA256(password, salt, iterations=480000, length=32)
```

---

## Vulnerability Disclosure Timeline

We follow a 90-day coordinated disclosure policy:

1. **Days 1-3**: Acknowledge receipt of vulnerability report
2. **Days 4-45**: Investigate and develop fix
3. **Days 46-90**: Test fix, prepare security advisory, and coordinate with maintainers
4. **Day 91**: Public disclosure and release of patched version

---

## Known Limitations

### Design Limitations

- **Plaintext Filenames**: The `.encrypted` extension reveals the file was encrypted
- **No Key Rotation**: Cannot rotate encryption keys without re-encrypting all files
- **Single Password**: All data encrypted with the same master password
- **No Access Control**: No built-in role-based access control (RBAC)

### Recommended Workarounds

1. **Hide Filenames**

   ```bash
   # Encrypt filename along with content
   tar czf - secret_file.pdf | vault encrypt /dev/stdin
   ```

2. **Key Rotation**

   ```bash
   # Decrypt all files with old key, re-encrypt with new key
   for file in *.encrypted; do
     vault decrypt "$file" --password "$OLD_KEY" --output "${file%.encrypted}"
     vault encrypt "${file%.encrypted}" --password "$NEW_KEY"
   done
   ```

3. **Per-User Encryption**
   ```bash
   # Derive per-user passwords from master password
   USER_PASSWORD=$(echo -n "user_123:$MASTER_PASSWORD" | sha256sum | cut -d' ' -f1)
   vault encrypt user_data.json --password "$USER_PASSWORD"
   ```

---

## Security Testing

### Manual Testing

```bash
# Test encryption/decryption roundtrip
echo "secret data" > test.txt
vault encrypt test.txt --password "test-key-123"
vault decrypt test.txt.encrypted --password "test-key-123" --output test_restored.txt
diff test.txt test_restored.txt

# Test wrong password rejection
vault decrypt test.txt.encrypted --password "wrong-password"  # Should fail

# Test file integrity
hexdump -C test.txt.encrypted | head -1  # Verify salt
```

### Automated Testing

```bash
pytest tests/test_crypto.py -v --cov=vault
```

### External Audits

- No third-party security audit has been conducted
- For production use with sensitive data, consider professional security review
- Report any findings to the security email above

---

## Compliance

### Standards Alignment

- **NIST SP 800-132**: PBKDF2 recommendations (480,000 iterations ✓)
- **NIST SP 800-38A**: AES-CBC mode usage
- **OWASP Top 10**: No known violations of current guidance

### Data Protection Regulations

- **GDPR**: Encryption is a valid safeguard for data protection
- **HIPAA**: Can be used for PHI protection (requires audit trail)
- **PCI-DSS**: Meets requirements for cardholder data encryption

---

## Security Roadmap

### Planned Improvements

- [ ] Support for key rotation without full re-encryption
- [ ] Asymmetric encryption option (RSA/ECDH)
- [ ] Hardware security module (HSM) integration
- [ ] Authenticated encryption with additional data (AEAD)
- [ ] Implement authenticated passwords (SRP)
- [ ] Official third-party security audit

### Future Considerations

- Consider post-quantum cryptography algorithms
- Add support for encrypted metadata
- Implement key escrow/recovery mechanisms
- Add rate limiting for brute-force protection

---

## Support

- **Security Questions**: security@[your-domain].com
- **Bug Reports**: [GitHub Issues](https://github.com/AmirhosseinOlyaei/vault-cli/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/AmirhosseinOlyaei/vault-cli/discussions)

---

## References

- [OWASP Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)
- [Cryptography.io - Hazmat Primitives](https://cryptography.io/en/latest/hazmat/primitives/)
- [NIST SP 800-132: Password-Based Key Derivation](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-132.pdf)
- [Fernet Specification](https://github.com/fernet/spec/blob/master/Spec.md)

---

**Last Updated**: 2026-09-27
**Version**: 1.0
