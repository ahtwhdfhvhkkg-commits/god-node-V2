import os
import json
import base64
import logging
from cryptography.fernet import Fernet
from typing import Dict, Any

logger = logging.getLogger("GodAuth")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
if not logger.handlers:
    logger.addHandler(handler)

# THE MAIN AUTH CLASS (This is what main.py is looking for!)
class GodAuth:
    """
    Enterprise-Grade Security Module for The God Node.
    Handles Fernet encryption, vault management, and master keys.
    """
    def __init__(self, vault_path="security_vault/secure_keys.json"):
        self.vault_path = vault_path
        self.master_key = os.environ.get("NEXUS_MASTER_KEY")

        if not self.master_key:
            # Generate temporary key if none provided in environment
            self.master_key = Fernet.generate_key().decode()
            logger.warning("No NEXUS_MASTER_KEY found in environment. Generated temporary key.")
            logger.warning("KEEP THIS KEY SECRET. DO NOT UPLOAD TO GITHUB.")

        self.cipher = Fernet(self.master_key.encode())
        self.keys_db = self._load_vault()
        logger.info("GodAuth initialized: Cryptographic shields are active.")

    def _load_vault(self) -> dict:
        """Loads data from the secure vault."""
        if not os.path.exists(self.vault_path):
            return {}
        try:
            with open(self.vault_path, "rb") as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    return {}
                decrypted_data = self.cipher.decrypt(encrypted_data).decode()
                return json.loads(decrypted_data)
        except Exception as e:
            logger.error(f"[SECURITY ALERT]: Vault corrupted or tampering detected! {e}")
            return {}

    def _save_vault(self):
        """Saves encrypted data back to the vault."""
        raw_data = json.dumps(self.keys_db).encode()
        encrypted_data = self.cipher.encrypt(raw_data)
        
        os.makedirs(os.path.dirname(self.vault_path), exist_ok=True)
        with open(self.vault_path, "wb") as f:
            f.write(encrypted_data)

    def store_secret(self, service_name: str, secret_value: str):
        """Securely stores a new API key or password."""
        self.keys_db[service_name] = secret_value
        self._save_vault()
        logger.info(f"Secret for '{service_name}' locked successfully.")

    def get_secret(self, service_name: str) -> str:
        """Retrieves a decrypted secret from the vault."""
        secret = self.keys_db.get(service_name)
        if not secret:
            raise ValueError(f"Secret for {service_name} not found in God Vault.")
        return secret
# Alias ताकि main.py बिना एरर के GodVault नाम से भी इसे चला सके
GodVault = GodAuth
        
