import os
import json
import logging
from cryptography.fernet import Fernet
from typing import Dict, Any

# Configure logging
logger = logging.getLogger("promptshield.secure_storage")

# File paths
KEY_FILE = "secret.key"
DATA_FILE = "secure_customers.enc"

class SecureStorage:
    def __init__(self):
        self.key = self._load_or_generate_key()
        self.cipher_suite = Fernet(self.key)
        self._ensure_data_file()

    def _load_or_generate_key(self) -> bytes:
        """Load the encryption key from file or generate a new one."""
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f:
                f.write(key)
            logger.info("Generated new encryption key for secure storage.")
            return key

    def _ensure_data_file(self):
        """Ensure the data file exists with valid empty JSON if not present."""
        if not os.path.exists(DATA_FILE):
            self._write_data({})

    def _read_data(self) -> Dict[str, Any]:
        """Read and decrypt the data from the file."""
        if not os.path.exists(DATA_FILE):
            return {}
        
        try:
            with open(DATA_FILE, "rb") as f:
                encrypted_data = f.read()
            
            if not encrypted_data:
                return {}

            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to read secure data: {e}")
            return {}

    def _write_data(self, data: Dict[str, Any]):
        """Encrypt and write data to the file."""
        try:
            json_data = json.dumps(data)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode('utf-8'))
            with open(DATA_FILE, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            logger.error(f"Failed to write secure data: {e}")

    def update_user(self, email: str, data: Dict[str, Any]):
        """
        Update or add a user's record securely.
        'data' should contain: password_hash, api_key, usage_count, max_usage, etc.
        """
        current_data = self._read_data()
        
        # If user exists, merge data
        if email in current_data:
            current_data[email].update(data)
        else:
            current_data[email] = data
            
        self._write_data(current_data)
        # logger.info(f"Securely updated record for {email}")

    def get_user(self, email: str) -> Dict[str, Any]:
        data = self._read_data()
        return data.get(email, {})

# Singleton instance
secure_storage = SecureStorage()
