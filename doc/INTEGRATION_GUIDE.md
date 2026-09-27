# Integration Guide: Using Vault Across System Architecture

This guide covers how to invoke Vault in other applications and explores use cases across different layers of system architecture—from infrastructure to application.

## Table of Contents

1. [Invocation Methods](#invocation-methods)
2. [Infrastructure Layer](#infrastructure-layer)
3. [DevOps/CI-CD Layer](#devopsci-cd-layer)
4. [Application Layer](#application-layer)
5. [Integration Patterns](#integration-patterns)

---

## Invocation Methods

### Method 1: Command-Line Interface (CLI)

Invoke Vault directly from shell scripts, cron jobs, or any system that can execute shell commands.

```bash
# Encrypt a file
vault encrypt /path/to/file.txt --password "secret-key"

# Decrypt a file
vault decrypt /path/to/file.txt.encrypted --password "secret-key" --output /path/to/restored.txt

# In shell scripts
encrypt_config() {
  local config_file=$1
  local password=$2
  vault encrypt "$config_file" --password "$password"
  rm "$config_file"  # Optional: delete plaintext
}

encrypt_config /etc/app/config.yml "prod-key-123"
```

### Method 2: Python Library Import

Use Vault as a Python library in your application.

```python
from vault.crypto import encrypt_file, decrypt_file

# Encrypt
encrypted_path = encrypt_file("sensitive_data.json", "my-password")
print(f"Encrypted to: {encrypted_path}")

# Decrypt
plaintext = decrypt_file("sensitive_data.json.encrypted", "my-password")
with open("restored.json", "wb") as f:
    f.write(plaintext)
```

### Method 3: Wrapper Functions

Create custom wrapper functions for application-specific needs.

```python
# app/security.py
from vault.crypto import encrypt_file, decrypt_file
import os

class VaultManager:
    def __init__(self, master_password: str):
        self.master_password = master_password

    def encrypt_user_data(self, user_id: str, data_file: str) -> str:
        """Encrypt user data with user-specific naming."""
        encrypted_path = encrypt_file(data_file, self.master_password)
        user_encrypted_path = f"data/users/{user_id}/{encrypted_path}"
        os.makedirs(os.path.dirname(user_encrypted_path), exist_ok=True)
        os.rename(encrypted_path, user_encrypted_path)
        return user_encrypted_path

    def decrypt_user_data(self, encrypted_path: str) -> bytes:
        """Decrypt user data with validation."""
        if not encrypted_path.endswith(".encrypted"):
            raise ValueError("Invalid encrypted file")
        return decrypt_file(encrypted_path, self.master_password)

# Usage
vault = VaultManager("app-master-key")
vault.encrypt_user_data("user_123", "user_profile.json")
```

### Method 4: REST API Wrapper

Expose Vault functionality via HTTP API.

```python
# api/encryption_service.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from vault.crypto import encrypt_file, decrypt_file
import tempfile
import os

app = FastAPI()

@app.post("/encrypt")
async def encrypt_endpoint(file: UploadFile, password: str):
    """Encrypt a file via HTTP."""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp.flush()

            encrypted_path = encrypt_file(tmp.name, password)
            with open(encrypted_path, "rb") as enc_file:
                return {"filename": file.filename, "data": enc_file.read()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/decrypt")
async def decrypt_endpoint(file: UploadFile, password: str):
    """Decrypt a file via HTTP."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".encrypted", delete=False) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp.flush()

            plaintext = decrypt_file(tmp.name, password)
            return {"filename": file.filename.replace(".encrypted", ""), "data": plaintext}
    except ValueError:
        raise HTTPException(status_code=401, detail="Wrong password")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Infrastructure Layer

### Use Case 1: Database Backup Encryption

Encrypt backups automatically and store securely.

```bash
#!/bin/bash
# backup_and_encrypt.sh

BACKUP_DIR="/backups"
DB_NAME="production_db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql"
VAULT_PASSWORD="$VAULT_MASTER_PASSWORD"

# Create backup
mysqldump -u root -p"$DB_PASSWORD" "$DB_NAME" > "$BACKUP_FILE"

# Encrypt backup
vault encrypt "$BACKUP_FILE" --password "$VAULT_PASSWORD"

# Delete plaintext backup
rm "$BACKUP_FILE"

# Upload encrypted backup to S3
aws s3 cp "${BACKUP_FILE}.encrypted" s3://backups/production/

echo "✓ Backup encrypted and uploaded"
```

### Use Case 2: Configuration File Encryption

Encrypt sensitive configuration files.

```bash
#!/bin/bash
# encrypt_configs.sh

CONFIG_DIR="/etc/app"
ENCRYPTION_KEY="config-encryption-key-$(date +%Y)"

for config in "$CONFIG_DIR"/*.yml; do
  if [[ ! "$config" =~ ".encrypted" ]]; then
    vault encrypt "$config" --password "$ENCRYPTION_KEY"
    rm "$config"  # Keep only encrypted version
  fi
done

echo "✓ All configs encrypted"
```

**Application startup:**

```bash
# decrypt_configs.sh
CONFIG_DIR="/etc/app"
ENCRYPTION_KEY="config-encryption-key-$(date +%Y)"

for encrypted_config in "$CONFIG_DIR"/*.encrypted; do
  vault decrypt "$encrypted_config" --password "$ENCRYPTION_KEY" \
    --output "${encrypted_config%.encrypted}"
done

# Start application with decrypted configs
python app/main.py
```

### Use Case 3: Log File Encryption

Encrypt sensitive logs before archival.

```python
# infrastructure/log_encryption.py
import logging
import os
from vault.crypto import encrypt_file
from datetime import datetime

class EncryptedFileHandler(logging.FileHandler):
    def __init__(self, filename, password):
        super().__init__(filename)
        self.password = password

    def emit(self, record):
        super().emit(record)
        # Encrypt when file rotates
        if os.path.getsize(self.baseFilename) > 100_000_000:  # 100MB
            encrypt_file(self.baseFilename, self.password)
            self.stream = open(self.baseFilename, 'a')

# Usage
logger = logging.getLogger(__name__)
logger.addHandler(EncryptedFileHandler("app.log", "log-encryption-key"))
```

---

## DevOps/CI-CD Layer

### Use Case 1: Secret Management in CI/CD Pipelines

Encrypt secrets and decrypt during deployment.

```yaml
# .github/workflows/deploy.yml
name: Deploy

on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Vault
        run: pip install vault-cli # Assuming published to PyPI

      - name: Decrypt secrets
        env:
          VAULT_PASSWORD: ${{ secrets.VAULT_PASSWORD }}
        run: |
          vault decrypt secrets/prod.env.encrypted \
            --password "$VAULT_PASSWORD" \
            --output secrets/prod.env

      - name: Deploy
        run: |
          source secrets/prod.env
          docker build -t app:${{ github.sha }} .
          docker push myregistry/app:${{ github.sha }}

          # Clean up plaintext secrets
          rm secrets/prod.env
```

### Use Case 2: Artifact Encryption

Encrypt build artifacts and container images.

```bash
#!/bin/bash
# ci/encrypt_artifacts.sh

BUILD_ARTIFACTS_DIR="build/"
ENCRYPTION_KEY="$CI_ARTIFACT_KEY"

# Encrypt all artifacts
for artifact in "$BUILD_ARTIFACTS_DIR"/*; do
  vault encrypt "$artifact" --password "$ENCRYPTION_KEY"
done

# Upload encrypted artifacts
aws s3 sync "$BUILD_ARTIFACTS_DIR" s3://artifacts/ --include "*.encrypted"
```

### Use Case 3: Environment Variable Encryption

Manage encrypted environment variables for different stages.

```bash
#!/bin/bash
# ci/manage_secrets.sh

STAGE=$1  # dev, staging, prod
SECRETS_FILE="secrets/${STAGE}.env"

# Encrypt before commit
if [[ -f "$SECRETS_FILE" ]]; then
  vault encrypt "$SECRETS_FILE" \
    --password "stage-${STAGE}-key-$(date +%Y)"
  git add "$SECRETS_FILE.encrypted"
  rm "$SECRETS_FILE"
fi
```

---

## Application Layer

### Use Case 1: User Data Encryption

Encrypt sensitive user information at application level.

```python
# models/user.py
from vault.crypto import encrypt_file, decrypt_file
import json
import tempfile
import os

class User:
    def __init__(self, user_id, app_password):
        self.user_id = user_id
        self.app_password = app_password

    def save_encrypted_profile(self, profile_data: dict, storage_path: str):
        """Save user profile encrypted."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            json.dump(profile_data, tmp)
            tmp.flush()

            encrypted_path = encrypt_file(tmp.name, self.app_password)
            final_path = f"{storage_path}/user_{self.user_id}.json.encrypted"
            os.rename(encrypted_path, final_path)
            os.unlink(tmp.name)

            return final_path

    def load_encrypted_profile(self, encrypted_path: str) -> dict:
        """Load user profile decrypted."""
        plaintext = decrypt_file(encrypted_path, self.app_password)
        return json.loads(plaintext.decode())

# Usage
user = User("user_123", app_password="derived-user-key")
user.save_encrypted_profile(
    {"name": "John Doe", "email": "john@example.com", "phone": "+1234567890"},
    "/data/profiles"
)
```

### Use Case 2: Document Management System

Encrypt uploaded documents.

```python
# app/document_service.py
from vault.crypto import encrypt_file, decrypt_file
from flask import Flask, request, send_file
import os

app = Flask(__name__)
UPLOAD_DIR = "uploads"

@app.route("/upload", methods=["POST"])
def upload_document():
    """Upload and encrypt document."""
    file = request.files["document"]
    user_id = request.form["user_id"]
    password = request.form["password"]

    # Save temporary file
    temp_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(temp_path)

    # Encrypt
    encrypted_path = encrypt_file(temp_path, password)
    final_path = f"{UPLOAD_DIR}/{user_id}/{encrypted_path}"
    os.makedirs(os.path.dirname(final_path), exist_ok=True)
    os.rename(encrypted_path, final_path)
    os.unlink(temp_path)

    return {"encrypted_path": final_path, "status": "uploaded"}

@app.route("/download/<user_id>/<doc_id>", methods=["GET"])
def download_document(user_id, doc_id):
    """Download and decrypt document."""
    password = request.args.get("password")
    encrypted_path = f"{UPLOAD_DIR}/{user_id}/{doc_id}.encrypted"

    try:
        plaintext = decrypt_file(encrypted_path, password)
        return send_file(
            io.BytesIO(plaintext),
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name=doc_id
        )
    except ValueError:
        return {"error": "Invalid password"}, 401
```

### Use Case 3: Cache Encryption

Encrypt sensitive cache entries.

```python
# app/cache.py
from vault.crypto import encrypt_file, decrypt_file
from functools import wraps
import tempfile
import json

class EncryptedCache:
    def __init__(self, cache_dir: str, password: str):
        self.cache_dir = cache_dir
        self.password = password

    def get(self, key: str):
        """Retrieve decrypted cache entry."""
        encrypted_path = f"{self.cache_dir}/{key}.encrypted"
        if not os.path.exists(encrypted_path):
            return None

        plaintext = decrypt_file(encrypted_path, self.password)
        return json.loads(plaintext.decode())

    def set(self, key: str, value):
        """Store encrypted cache entry."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            json.dump(value, tmp)
            tmp.flush()

            encrypted_path = encrypt_file(tmp.name, self.password)
            final_path = f"{self.cache_dir}/{key}.encrypted"
            os.rename(encrypted_path, final_path)
            os.unlink(tmp.name)

# Decorator for automatic caching
def encrypted_cache(cache_dir: str, password: str):
    cache = EncryptedCache(cache_dir, password)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"

            # Try to get from cache
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

            # Compute and cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        return wrapper
    return decorator

# Usage
@encrypted_cache("cache/", "cache-password")
def expensive_computation(x, y):
    return x ** y + y ** x
```

---

## Integration Patterns

### Pattern 1: Key Management

```python
# security/key_manager.py
import os
from cryptography.fernet import Fernet

class KeyManager:
    """Manage encryption keys securely."""

    @staticmethod
    def get_key(key_id: str) -> str:
        """Get key from environment or key store."""
        # Never hardcode keys
        return os.getenv(f"VAULT_KEY_{key_id}")

    @staticmethod
    def rotate_keys(old_key: str, new_key: str, file_list: list):
        """Rotate keys across files."""
        from vault.crypto import encrypt_file, decrypt_file

        for file_path in file_list:
            # Decrypt with old key
            plaintext = decrypt_file(file_path, old_key)

            # Re-encrypt with new key
            temp_file = f"{file_path}.tmp"
            with open(temp_file, "wb") as f:
                f.write(plaintext)

            os.unlink(file_path)
            encrypt_file(temp_file, new_key)

# Usage
KeyManager.rotate_keys(
    old_key=os.getenv("OLD_KEY"),
    new_key=os.getenv("NEW_KEY"),
    file_list=["data/user_1.encrypted", "data/user_2.encrypted"]
)
```

### Pattern 2: Error Handling

```python
# utils/vault_utils.py
from vault.crypto import encrypt_file, decrypt_file
import logging

logger = logging.getLogger(__name__)

def safe_encrypt(file_path: str, password: str) -> bool:
    """Encrypt with error handling."""
    try:
        encrypt_file(file_path, password)
        logger.info(f"Encrypted: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Encryption failed for {file_path}: {e}")
        return False

def safe_decrypt(encrypted_path: str, password: str) -> bytes | None:
    """Decrypt with error handling."""
    try:
        plaintext = decrypt_file(encrypted_path, password)
        logger.info(f"Decrypted: {encrypted_path}")
        return plaintext
    except ValueError as e:
        logger.error(f"Wrong password for {encrypted_path}")
        return None
    except Exception as e:
        logger.error(f"Decryption failed for {encrypted_path}: {e}")
        return None
```

### Pattern 3: Batch Processing

```python
# batch/encrypt_batch.py
import concurrent.futures
from vault.crypto import encrypt_file
from pathlib import Path

def encrypt_directory(directory: str, password: str, max_workers: int = 4):
    """Encrypt all files in directory using thread pool."""
    files = list(Path(directory).rglob("*"))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(encrypt_file, str(f), password)
            for f in files if f.is_file()
        ]

        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                encrypted_path = future.result()
                results.append({"status": "success", "path": encrypted_path})
            except Exception as e:
                results.append({"status": "error", "error": str(e)})

    return results

# Usage
results = encrypt_directory("/data/backup", "backup-password", max_workers=8)
print(f"Encrypted {len([r for r in results if r['status'] == 'success'])} files")
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  ┌──────────────────┬──────────────┬────────────────────┐   │
│  │ User Data        │ Documents    │ Sensitive Cache    │   │
│  │ Encryption       │ Management   │ Encryption         │   │
│  └──────────────────┴──────────────┴────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│                   Application/API Layer                      │
│  ┌──────────────────┬──────────────┬────────────────────┐   │
│  │ REST Wrapper     │ Python Lib   │ Custom Functions   │   │
│  └──────────────────┴──────────────┴────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│                    Vault Core Library                        │
│  ┌──────────────────┬────────────────────────────────────┐  │
│  │ encrypt_file()   │ decrypt_file()                     │  │
│  │ PBKDF2 + AES     │ Fernet + HMAC                      │  │
│  └──────────────────┴────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│              Infrastructure/DevOps Layer                     │
│  ┌──────────────────┬──────────────┬────────────────────┐   │
│  │ DB Backup        │ Config Files │ CI/CD Secrets      │   │
│  │ Encryption       │ Encryption   │ Encryption         │   │
│  └──────────────────┴──────────────┴────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Best Practices

1. **Key Management**
   - Store keys in environment variables, not code
   - Rotate keys periodically
   - Use separate keys for different data classifications

2. **Error Handling**
   - Log encryption/decryption failures
   - Never expose passwords in error messages
   - Implement retry logic with exponential backoff

3. **Performance**
   - Cache decrypted data when possible
   - Use batch processing for multiple files
   - Consider async/concurrent processing

4. **Security**
   - Verify password strength before encryption
   - Clean up temporary plaintext files
   - Use strong, unique passwords per data type
   - Never hardcode passwords

5. **Monitoring**
   - Track encryption/decryption metrics
   - Alert on repeated wrong password attempts
   - Monitor key rotation processes

---

## Summary

Vault can be integrated at multiple levels:

- **Infrastructure**: Database backups, config files, logs
- **DevOps**: CI/CD secrets, artifact encryption, deployments
- **Application**: User data, documents, caches, sensitive records

Choose the integration pattern that best fits your architecture and security requirements.
