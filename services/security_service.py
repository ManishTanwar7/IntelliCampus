"""
IntelliCampus: Security & Credential Encryption Service
Implements AES Fernet symmetric encryption for sensitive student credentials.
"""
import base64
import os
import hashlib
from cryptography.fernet import Fernet
from config import SECURITY_KEY_FILE

class SecurityService:
    _key: bytes = None

    @classmethod
    def _get_or_create_key(cls) -> bytes:
        if cls._key is not None:
            return cls._key

        if SECURITY_KEY_FILE.exists():
            try:
                with open(SECURITY_KEY_FILE, "rb") as f:
                    cls._key = f.read().strip()
                if len(cls._key) > 0:
                    return cls._key
            except Exception:
                pass

        # Generate new Fernet key
        new_key = Fernet.generate_key()
        try:
            with open(SECURITY_KEY_FILE, "wb") as f:
                f.write(new_key)
        except Exception as e:
            print(f"[SecurityService] Could not persist secret key: {e}")
        cls._key = new_key
        return cls._key

    @classmethod
    def encrypt_password(cls, plain_password: str) -> tuple[str, str]:
        """
        Encrypts a password with Fernet and returns (encrypted_token, salt).
        """
        key = cls._get_or_create_key()
        f = Fernet(key)
        salt = os.urandom(16).hex()
        # Combine password with salt
        salted = f"{salt}:{plain_password}"
        encrypted = f.encrypt(salted.encode("utf-8")).decode("utf-8")
        return encrypted, salt

    @classmethod
    def decrypt_password(cls, encrypted_password: str, salt: str) -> str:
        """
        Decrypts an encrypted password using the secret key.
        """
        key = cls._get_or_create_key()
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_password.encode("utf-8")).decode("utf-8")
        if decrypted.startswith(f"{salt}:"):
            return decrypted[len(salt) + 1:]
        return decrypted

    @classmethod
    def hash_token(cls, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
