import os
import json
from cryptography.fernet import Fernet

class GodVault:
    def __init__(self, vault_path="security_vault/secure_keys.json"):
        self.vault_path = vault_path
        # .env फाइल या सर्वर के एनवायरनमेंट से मास्टर एन्क्रिप्शन की (Key) उठाएगा
        # अगर नहीं मिलेगी, तो यह खुद को लॉक कर लेगा
        self.master_key = os.environ.get("NEXUS_MASTER_KEY")
        
        if not self.master_key:
            # लोकल टेस्टिंग के लिए नई की (Key) बनाना (सर्वर पर इसे एनवायरनमेंट वेरिएबल में डालना होगा)
            self.master_key = Fernet.generate_key().decode()
            print(f"[WARNING]: No NEXUS_MASTER_KEY found in environment. Generated temporary key: {self.master_key}")
            print("[WARNING]: KEEP THIS KEY SECRET. DO NOT UPLOAD TO GITHUB.")
        
        self.cipher = Fernet(self.master_key.encode())
        self.keys_db = self._load_vault()

    def _load_vault(self) -> dict:
        """तिजोरी (Vault) से डेटा लोड करना"""
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
            print(f"[SECURITY ALERT]: Vault corrupted or tampering detected! {e}")
            return {}

    def _save_vault(self):
        """डेटा को एन्क्रिप्ट करके वापस तिजोरी में सेव करना"""
        raw_data = json.dumps(self.keys_db).encode()
        encrypted_data = self.cipher.encrypt(raw_data)
        
        os.makedirs(os.path.dirname(self.vault_path), exist_ok=True)
        with open(self.vault_path, "wb") as f:
            f.write(encrypted_data)

    def store_secret(self, service_name: str, secret_value: str):
        """किसी भी नई API की (Key) या पासवर्ड को एन्क्रिप्ट करके सेव करना"""
        self.keys_db[service_name] = secret_value
        self._save_vault()
        print(f"[VAULT]: Secret for '{service_name}' locked successfully.")

    def get_secret(self, service_name: str) -> str:
        """रनटाइम पर (जब सर्वर को जरूरत हो) की (Key) को डीकोड करके देना"""
        secret = self.keys_db.get(service_name)
        if not secret:
            raise ValueError(f"Secret for {service_name} not found in God Vault.")
        return secret
      
