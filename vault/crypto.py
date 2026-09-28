import os
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import urlsafe_b64encode

logger = logging.getLogger(__name__)


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a encryption key from password using PBKDF2."""
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = kdf.derive(password.encode())
        logger.debug("Key derived successfully")
        return urlsafe_b64encode(key)
    except Exception as e:
        logger.error(f"Key derivation failed: {e}")
        raise


def encrypt_file(filepath: str, password: str) -> str:
    """Encrypt a file and return the encrypted filepath."""
    try:
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"File not found: {filepath}")

        logger.info(f"Encrypting file: {filepath}")
        salt = os.urandom(16)
        key = derive_key(password, salt)
        cipher = Fernet(key)

        with open(filepath, "rb") as f:
            plaintext = f.read()

        logger.debug(f"Read {len(plaintext)} bytes from {filepath}")
        ciphertext = cipher.encrypt(plaintext)
        encrypted_data = salt + ciphertext

        encrypted_path = filepath + ".encrypted"
        with open(encrypted_path, "wb") as f:
            f.write(encrypted_data)

        logger.info(f"File encrypted successfully: {encrypted_path}")
        return encrypted_path

    except Exception as e:
        logger.error(f"Encryption failed for {filepath}: {e}")
        raise


def decrypt_file(encrypted_path: str, password: str) -> bytes:
    """Decrypt a file and return plaintext."""
    try:
        if not os.path.exists(encrypted_path):
            logger.error(f"Encrypted file not found: {encrypted_path}")
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_path}")

        logger.info(f"Decrypting file: {encrypted_path}")

        with open(encrypted_path, "rb") as f:
            encrypted_data = f.read()

        salt = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        key = derive_key(password, salt)
        cipher = Fernet(key)

        plaintext = cipher.decrypt(ciphertext)
        logger.info(f"File decrypted successfully: {encrypted_path}")
        logger.debug(f"Decrypted {len(plaintext)} bytes")
        return plaintext

    except ValueError as e:
        logger.warning(f"Decryption failed (invalid password?): {encrypted_path}")
        raise ValueError("Decryption failed. Wrong password?") from e
    except Exception as e:
        logger.error(f"Decryption failed for {encrypted_path}: {e}")
        raise
