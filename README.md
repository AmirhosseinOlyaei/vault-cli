# Vault — Secure File Encryption CLI

A lightweight, command-line tool for encrypting and decrypting files with password-based security. Built with industry-standard cryptography, powered by OpenSSL and the Python `cryptography` library.

## Features

- 🔐 **AES Encryption**: Uses Fernet (symmetric encryption) with 128-bit keys
- 🔑 **Secure Key Derivation**: PBKDF2 with SHA256 (480,000 iterations)
- 🛡️ **Security Scanning**: Semgrep Guardian continuously scans for vulnerabilities
- 🧹 **Auto Cleanup**: Stop hooks automatically remove temporary files on exit
- ⚡ **Simple CLI**: Intuitive command-line interface with password prompts
- ✅ **Cross-platform**: Works on macOS, Linux, and Windows

## Requirements

- Python 3.9+
- OpenSSL (installed via Homebrew or system package manager)
- pkg-config (for locating OpenSSL)

## Installation

### Prerequisites

```bash
# macOS with Homebrew
brew install pkgconf openssl

# Ubuntu/Debian
sudo apt-get install libssl-dev pkg-config

# Fedora/RHEL
sudo dnf install openssl-devel pkgconf
```

### Install Vault

```bash
# Clone or navigate to the project
cd /path/to/vault

# Install in development mode
pip install -e .

# Verify installation
vault --help
```

## Usage

### Encrypt a File

```bash
vault encrypt path/to/file.txt

# Enter password when prompted (twice for confirmation)
# Output: path/to/file.txt.encrypted
```

Or provide password directly:

```bash
vault encrypt myfile.txt --password "my-secure-password"
```

### Decrypt a File

```bash
vault decrypt path/to/file.txt.encrypted

# Enter password when prompted
# Output: path/to/file.txt
```

Specify custom output path:

```bash
vault decrypt path/to/file.txt.encrypted --password "my-secure-password" --output restored.txt
```

## How It Works

### Encryption Process

1. Generate a random 16-byte salt
2. Derive a 256-bit key from the password using PBKDF2-SHA256 (480,000 iterations)
3. Encrypt the file using AES via Fernet
4. Prepend the salt to the ciphertext
5. Write the combined data to a `.encrypted` file

### Decryption Process

1. Read the `.encrypted` file and extract the salt (first 16 bytes)
2. Derive the key using the same password and salt
3. Decrypt the remaining ciphertext using Fernet
4. Write the plaintext to the output file

## Security Considerations

### Strengths

- ✅ **PBKDF2 iteration count**: 480,000 iterations resists brute-force attacks
- ✅ **Fernet**: Uses AES-128 in CBC mode with HMAC authentication
- ✅ **Random salt**: Unique salt per file prevents rainbow table attacks
- ✅ **Secure key derivation**: SHA256 hashing with cryptographic salt

### Best Practices

- Use strong, unique passwords (16+ characters with mixed case, numbers, symbols)
- Store encrypted files in secure locations (cloud backups, encrypted drives)
- Never share unencrypted plaintext after encryption
- Test decryption before deleting original files
- Regularly backup your `.encrypted` files

### Limitations

- ⚠️ Password strength depends on user input
- ⚠️ Does not provide digital signatures (cannot verify file integrity without decryption)
- ⚠️ Plaintext filename is visible in the `.encrypted` filename

## Examples

### Example 1: Encrypt a Document

```bash
$ vault encrypt important_doc.pdf

Password: ••••••••••••••••
Confirm password: ••••••••••••••••
✓ Encrypted: important_doc.pdf.encrypted

$ rm important_doc.pdf  # Safe to delete original
```

### Example 2: Share and Decrypt

```bash
# Recipient receives important_doc.pdf.encrypted
$ vault decrypt important_doc.pdf.encrypted

Password: ••••••••••••••••
✓ Decrypted: important_doc.pdf
```

### Example 3: Batch Encryption (Manual Loop)

```bash
for file in *.txt; do
  vault encrypt "$file" --password "batch-password"
done
```

## Project Structure

```
vault/
├── __init__.py          # Package initialization
├── crypto.py            # Encryption/decryption logic
└── cli.py               # Command-line interface
.claude/
├── hooks.toml           # Auto-cleanup stop hooks
pyproject.toml           # Project metadata and dependencies
README.md                # This file
```

## Development

### Run Tests

```bash
# Create a test file
echo "Secret content" > test.txt

# Encrypt and decrypt
vault encrypt test.txt --password "test123"
vault decrypt test.txt.encrypted --password "test123" --output test_decrypted.txt

# Verify
cat test_decrypted.txt
# Output: Secret content
```

### Code Quality

- **Semgrep Guardian**: Continuously scans for security vulnerabilities
- **Stop Hooks**: Auto-cleanup of temporary files and cache
- **Type Hints**: Type annotations throughout the codebase

## Troubleshooting

### "Decryption failed. Wrong password?"

- Verify you're using the correct password
- Ensure the `.encrypted` file wasn't corrupted
- Try decrypting on the same system where you encrypted

### "Could not find openssl via pkg-config"

```bash
# Set OPENSSL_DIR manually
export OPENSSL_DIR=$(brew --prefix openssl)

# Then try again
vault encrypt myfile.txt --password "secret"
```

### "ImportError: cannot import name 'PBKDF2'"

Ensure cryptography is installed:

```bash
pip install cryptography>=41.0.0
```

## License

MIT

## Contributing

Contributions welcome! Please ensure:

- Code passes Semgrep security scanning
- Functions have type hints
- Error messages are user-friendly

## Author

- Built with Claude Code · [Learn more](https://claude.com/claude-code) @ DevArts Lab .·•° [devartslab.com](https://devartslab.com)
