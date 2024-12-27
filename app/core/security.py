import json
import logging
import os
from dataclasses import dataclass
from secrets import token_hex
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers.base import CipherContext
from .settings import ENV_FILE_PATH
@dataclass
class CryptoConfig:
    key_length: int = 16 
    block_size: int = 16

class SecretKeyManager:
    def __init__(self, env_file_path) -> None:
        self.env_file_path = env_file_path
        self.secret_key = self._load_or_generate_key()

    def _load_or_generate_key(self) -> str:
        """Load existing secret key or generate a new one."""
        key: str | None = os.getenv('SECRET_KEY')
        if not key:
            key = self._generate_secret_key()
            self._save_secret_key(key)
        return key

    def _generate_secret_key(self) -> str:
        """Generate a new cryptographically secure secret key."""
        return token_hex(CryptoConfig.key_length)

    def _save_secret_key(self, key: str) -> None:
        """Save the secret key to the environment file."""
        try:
            with open(self.env_file_path, 'a+') as env_file:
                env_file.write(f"\nSECRET_KEY={key}")
            logging.info("New secret key saved to environment.")
        except Exception as e:
            logging.error(msg=f"Failed to save secret key: {e}")
            raise

class DataCrypto:
    def __init__(self, secret_key: str) -> None:
        self.key: bytes = bytes.fromhex(secret_key)
        self.config = CryptoConfig()

    def encrypt(self, data: Dict[str, Any]) -> Optional[bytes]:
        """Encrypt a dictionary to bytes."""
        try:
            json_data: str = json.dumps(data)
            iv: bytes = os.urandom(self.config.block_size)
            padder: padding.PaddingContext = padding.PKCS7(algorithms.AES.block_size).padder()
            
            padded_data: bytes = padder.update(json_data.encode()) + padder.finalize()
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            
            encryptor: CipherContext = cipher.encryptor()
            encrypted_data: bytes = encryptor.update(padded_data) + encryptor.finalize()
            
            return iv + encrypted_data
        except Exception as e:
            logging.error(f"Encryption error: {e}")
            return None

    def decrypt(self, encrypted_data: bytes) -> Optional[Dict[str, Any]]:
        """Decrypt bytes to a dictionary."""
        try:
            iv: bytes = encrypted_data[:self.config.block_size]
            ciphertext: bytes = encrypted_data[self.config.block_size:]
            
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            decryptor: CipherContext = cipher.decryptor()
            
            decrypted_padded: bytes = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder: padding.PaddingContext = padding.PKCS7(algorithms.AES.block_size).unpadder()
            
            decrypted_data: bytes = unpadder.update(decrypted_padded) + unpadder.finalize()
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            return None

# Usage
try:
    secret_key_manager = SecretKeyManager(ENV_FILE_PATH)
    crypto = DataCrypto(secret_key_manager.secret_key)
    
    data: Dict[str, str] = {"sensitive": "information"}
    encrypted: bytes | None = crypto.encrypt(data)
    decrypted: Dict[str, Any] | None = crypto.decrypt(encrypted)
except Exception as e:
    logging.error(f"Crypto initialization error: {e}")
    raise
