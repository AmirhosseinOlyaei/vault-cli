import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import urlsafe_b64encode


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a encryption key from password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = kdf.derive(password.encode())
    return urlsafe_b64encode(key)


def encrypt_file(filepath: str, password: str) -> str:
    """Encrypt a file and return the encrypted filepath."""
    salt = os.urandom(16)
    key = derive_key(password, salt)
    cipher = Fernet(key)

    with open(filepath, "rb") as f:
        plaintext = f.read()

    ciphertext = cipher.encrypt(plaintext)
    encrypted_data = salt + ciphertext

    encrypted_path = filepath + ".encrypted"
    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data)

    return encrypted_path


def decrypt_file(encrypted_path: str, password: str) -> bytes:
    """Decrypt a file and return plaintext."""
    with open(encrypted_path, "rb") as f:
        encrypted_data = f.read()

    salt = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    key = derive_key(password, salt)
    cipher = Fernet(key)

    try:
        plaintext = cipher.decrypt(ciphertext)
        return plaintext
    except Exception as e:
        raise ValueError("Decryption failed. Wrong password?") from e
