"""
cloud_storage/db_manager.py

Asynchronous Database Manager for God Node.
Handles persistent storage of player states, economy, and AI memory.
Designed to safely write data to disk/cloud without blocking the main game loop.
"""

import asyncio
import json
import os
import aiofiles # Asynchronous file operations के लिए
from typing import Dict, Any, Optional

class AsyncDatabaseVault:
    def __init__(self, storage_path: str = "./local_cloud_data"):
        # यह वो मेन फोल्डर है जहाँ सारा डेटा सेव होगा
        self.storage_path = storage_path
        self.players_dir = os.path.join(self.storage_path, "players")
        self.world_dir = os.path.join(self.storage_path, "world_state")
        
        # अगर फोल्डर नहीं हैं, तो उन्हें तुरंत बना दो
        os.makedirs(self.players_dir, exist_ok=True)
        os.makedirs(self.world_dir, exist_ok=True)
        
        print(f"[CLOUD STORAGE] Vault Initialized at: {self.storage_path}")

    async def save_player_data(self, player_id: str, data: Dict[str, Any]) -> bool:
        """
        खिलाड़ी का डेटा (स्थिति, पैसा, हेल्थ) हार्ड-डिस्क/क्लाउड में सेव करना।
        यह 'aiofiles' का इस्तेमाल करता है ताकि 30,000 प्लेयर्स का डेटा सेव करते वक्त सर्वर हैंग न हो।
        """
        file_path = os.path.join(self.players_dir, f"{player_id}.json")
        try:
            # बैकग्राउंड में फाइल को लिखना (Zero Blocking)
            async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
                json_data = json.dumps(data, indent=2)
                await f.write(json_data)
            return True
        except Exception as e:
            print(f"[CLOUD ERROR] Failed to save player {player_id}: {e}")
            return False

    async def load_player_data(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        जब खिलाड़ी वापस गेम में आए, तो उसका पुराना डेटा लोड करना।
        """
        file_path = os.path.join(self.players_dir, f"{player_id}.json")
        if not os.path.exists(file_path):
            # अगर नया खिलाड़ी है, तो खाली डेटा भेजो
            return None
            
        try:
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"[CLOUD ERROR] Failed to load player {player_id}: {e}")
            return None

    async def backup_world_snapshot(self, snapshot_id: str, world_data: Dict[str, Any]) -> bool:
        """
        पूरी दुनिया (NPCs, मौसम, AI दिमाग) का एक स्नैपशॉट (Backup) सेव करना।
        भविष्य में यही स्नैपशॉट तुम्हारे 5TB G-Drive में भेजा जाएगा।
        """
        file_path = os.path.join(self.world_dir, f"snapshot_{snapshot_id}.json")
        try:
            async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
                await f.write(json.dumps(world_data))
            print(f"[CLOUD BACKUP] World snapshot '{snapshot_id}' saved successfully.")
            return True
        except Exception as e:
            print(f"[CLOUD ERROR] World backup failed: {e}")
            return False

# ग्लोबल इंस्टेंस जिसे पूरे गेम में कहीं भी इस्तेमाल किया जा सकेगा
db_vault = AsyncDatabaseVault()
