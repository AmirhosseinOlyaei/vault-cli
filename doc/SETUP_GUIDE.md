# Setup Guide: Fresh macOS Installation

This guide covers everything you need to install on a brand new Mac to recreate the Vault file encryption application from scratch.

## **Step 1: System Prerequisites**

```bash
# Install Xcode Command Line Tools (required for building)
xcode-select --install

# Install Homebrew (macOS package manager)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## **Step 2: Essential Build Tools**

```bash
# Install OpenSSL and pkg-config (required for cryptography library)
brew install openssl pkgconf

# Add OpenSSL to environment (add to ~/.zshrc)
echo 'export OPENSSL_DIR=$(brew --prefix openssl)' >> ~/.zshrc
source ~/.zshrc
```

## **Step 3: Python Runtime**

```bash
# Install Python 3.9+ (Homebrew or pyenv)
brew install python@3.12

# Or use pyenv for version management
brew install pyenv
pyenv install 3.12.0
pyenv global 3.12.0
```

## **Step 4: Git (for cloning and version control)**

```bash
# Usually comes with Xcode, but ensure it's installed
brew install git

# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## **Step 5: Clone and Setup the Project**

```bash
# Clone the repository
git clone git@github.com:AmirhosseinOlyaei/vault-cli.git
cd vault-cli

# Install dependencies
pip install -e .

# Verify installation
vault --help
```

## **Optional: Development Tools**

```bash
# Claude Code CLI (for development)
npm install -g @anthropic-ai/claude-code

# Or use Claude Code desktop/web app

# IDE (choose one)
brew install --cask visual-studio-code
# or
brew install --cask jetbrains-pycharm-community
```

## **Verification Checklist**

After installation, verify everything works:

```bash
# Test each dependency
which python3 && python3 --version
which pkg-config && pkg-config --version
which git && git --version
echo $OPENSSL_DIR && ls $OPENSSL_DIR

# Test the cryptography library
python3 -c "import cryptography; print(f'✓ cryptography {cryptography.__version__}')"

# Test Vault CLI
vault --help
vault encrypt --help
vault decrypt --help
```

## **Complete Install Script** (All-in-one)

Save this as `install.sh` and run `bash install.sh`:

```bash
#!/bin/bash

# Install Xcode CLI
xcode-select --install 2>/dev/null || echo "Xcode already installed"

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" 2>/dev/null || echo "Homebrew already installed"

# Install dependencies
brew install openssl pkgconf python@3.12 git

# Set OpenSSL environment variable
echo 'export OPENSSL_DIR=$(brew --prefix openssl)' >> ~/.zshrc
source ~/.zshrc

# Clone and setup
git clone git@github.com:AmirhosseinOlyaei/vault-cli.git
cd vault-cli
pip install -e .

# Verify
echo "✓ Installation complete!"
vault --help
```

## **System Requirements Summary**

| Component | What | Why |
|-----------|------|-----|
| **Xcode CLI Tools** | Build compiler | Compile native extensions |
| **Homebrew** | Package manager | Install system dependencies |
| **OpenSSL** | Crypto library | TLS/cryptography backend |
| **pkg-config** | Library locator | Find OpenSSL installation |
| **Python 3.9+** | Runtime | Run the application |
| **Git** | Version control | Clone the repo |
| **pip** | Package manager | Install Python packages |

## **Time Estimate**

- Xcode CLI Tools: ~5-10 minutes
- Homebrew + tools: ~5 minutes
- Python + Git: ~2 minutes
- Vault setup: ~2 minutes
- **Total: ~15-20 minutes**

## **Troubleshooting**

### OpenSSL Not Found
```bash
# Set environment variable manually
export OPENSSL_DIR=$(brew --prefix openssl)
echo 'export OPENSSL_DIR=$(brew --prefix openssl)' >> ~/.zshrc
source ~/.zshrc
```

### Python Version Mismatch
```bash
# Check Python version
python3 --version

# Use specific version with pyenv
pyenv local 3.12.0
```

### Git SSH Issues
```bash
# Generate SSH key for GitHub
ssh-keygen -t ed25519 -C "your@email.com"

# Add to GitHub account at https://github.com/settings/keys
```

### Cryptography Build Failure
```bash
# Ensure all build tools are installed
brew install openssl pkgconf
export OPENSSL_DIR=$(brew --prefix openssl)

# Reinstall cryptography
pip install --force-reinstall cryptography
```

---

**That's everything!** A fresh Mac can go from zero to running Vault in under 20 minutes with this guide.
