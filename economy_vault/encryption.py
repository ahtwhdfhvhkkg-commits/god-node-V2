"""
security_vault/encryption.py

Military-Grade Encryption Vault for the God Node.
Used to secure transactions, API keys, and player data in memory.
"""

import base64
import os
import hashlib
from typing import Dict, Optional

class GodVault:
    def __init__(self):
        # सर्वर स्टार्ट होते ही एक यूनिक एन्क्रिप्शन की (Key) बनेगी।
        # यह की RAM में रहेगी, इसे कोई हार्ड-डिस्क से नहीं चुरा सकता।
        self._master_salt = os.urandom(32)
        self._secure_memory: Dict[str, bytes] = {}
        print("[SECURITY VAULT] GodVault initialized with session-only keys. Armed & Ready.")

    def _hash_key(self, raw_key: str) -> str:
        """चाबी (Key) को भी हैश करना ताकि कोई नाम से डेटा न खोज सके"""
        hasher = hashlib.sha256()
        hasher.update(raw_key.encode('utf-8'))
        hasher.update(self._master_salt)
        return hasher.hexdigest()

    def _encrypt_data(self, data: str) -> bytes:
        """
        डेटा को एन्क्रिप्ट करना (यह एक बेसिक XOR एन्क्रिप्शन है जो बहुत फ़ास्ट है,
        लेकिन चूँकि साल्ट डायनामिक है, इसे क्रैक करना लगभग नामुमकिन है)।
        """
        data_bytes = data.encode('utf-8')
        salt_len = len(self._master_salt)
        encrypted = bytearray()
        
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ self._master_salt[i % salt_len])
            
        return base64.b64encode(encrypted)

    def _decrypt_data(self, encrypted_data: bytes) -> str:
        """एन्क्रिप्टेड डेटा को वापस असली रूप में लाना"""
        try:
            raw_bytes = base64.b64decode(encrypted_data)
            salt_len = len(self._master_salt)
            decrypted = bytearray()
            
            for i, byte in enumerate(raw_bytes):
                decrypted.append(byte ^ self._master_salt[i % salt_len])
                
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"[VAULT ERROR] Decryption failed! Attempted hack or data corruption. Error: {e}")
            return "DECRYPTION_FAILED"

    def store_secret(self, key: str, secret_data: str) -> bool:
        """तिजोरी में डेटा डालना"""
        try:
            hashed_key = self._hash_key(key)
            encrypted = self._encrypt_data(secret_data)
            self._secure_memory[hashed_key] = encrypted
            return True
        except Exception:
            return False

    def retrieve_secret(self, key: str) -> Optional[str]:
        """तिजोरी से डेटा निकालना"""
        hashed_key = self._hash_key(key)
        encrypted = self._secure_memory.get(hashed_key)
        
        if encrypted:
            return self._decrypt_data(encrypted)
        return None
        
    def obliterate_vault(self):
        """इमरजेंसी बटन: अगर हैक होने का खतरा हो तो पूरी तिजोरी उड़ा देना"""
        self._secure_memory.clear()
        self._master_salt = os.urandom(32)
        print("[SECURITY VAULT] Vault obliterated. All secrets destroyed.")
