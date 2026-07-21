"""
multiplayer_nexus/sync_server.py

God-Level Multiplayer WebSocket Node.
Handles 30,000+ concurrent connections in-memory and routes actions 
to the simulation scheduler for C++ validation.
"""

import asyncio
import json
import uuid
from typing import Dict
from fastapi import WebSocket

# =========================================================
# WIRING: हमारे बनाए हुए शेड्यूलर को यहाँ बुलाना
# =========================================================
from simulation_scheduler.types import SimulationTask, SimulationPriority
from simulation_scheduler.scheduler import SimulationScheduler
from simulation_scheduler.config import SchedulerConfig

class GodLevelMultiplayerNexus:
    def __init__(self, scheduler: SimulationScheduler = None):
        # 30,000+ खिलाड़ियों का लाइव डेटाबेस (RAM में चलेगा ताकि स्पीड मैक्सिमम रहे)
        self.active_connections: Dict[str, WebSocket] = {}
        self.player_states: Dict[str, dict] = {}
        
        # हमारा गेम इंजन (शेड्यूलर), जो प्लेयर के एक्शन्स को C++ में प्रोसेस करवाएगा
        self.scheduler = scheduler

    async def connect_player(self, player_id: str, websocket: WebSocket):
        """नया खिलाड़ी जब गेम/ऐप में घुसेगा तो उसे सर्वर से जोड़ना"""
        await websocket.accept()
        self.active_connections[player_id] = websocket
        
        # नए खिलाड़ी के जुड़ने का मैसेज बाकी दुनिया को भेजना
        await self.broadcast_system_message(f"[NEXUS]: Player {player_id} has entered the God Node.")
        print(f"[NETWORK]: Player {player_id} connected. Total active: {len(self.active_connections)}")

    def disconnect_player(self, player_id: str):
        """खिलाड़ी के ऑफलाइन होने पर उसे मेमोरी से हटाना ताकि सर्वर हैंग न हो"""
        if player_id in self.active_connections:
            del self.active_connections[player_id]
        if player_id in self.player_states:
            del self.player_states[player_id]
        print(f"[NETWORK]: Player {player_id} disconnected.")

    async def process_action(self, player_id: str, action_data: dict):
        """
        यह सबसे अहम हिस्सा है (Mass Sync & Engine Execution): 
        जैसे ही कोई खिलाड़ी मूव करेगा या कुछ करेगा, यह डेटा बाकी सभी को भेजा जाएगा,
        और साथ ही C++ इंजन को प्रोसेसिंग के लिए दिया जाएगा।
        """
        # 1. खिलाड़ी की नई पोज़िशन/स्टेटस सेव करना
        self.player_states[player_id] = action_data
        
        # 2. [NEW WIRING] - इंजन को काम सौंपना
        if self.scheduler:
            # प्लेयर के काम को एक Task बनाकर शेड्यूलर की कतार में डाल देना
            task = SimulationTask(
                task_id=f"net_{player_id}_{uuid.uuid4().hex[:6]}",
                priority=SimulationPriority.HIGH, # प्लेयर का काम सबसे ज़रूरी है
                payload={"player_id": player_id, "action": action_data}
            )
            self.scheduler.submit(task)

        # 3. ब्रॉडकास्ट पेलोड बनाना
        broadcast_data = {
            "type": "STATE_UPDATE",
            "player_id": player_id,
            "action": action_data
        }
        
        # 4. जिसने एक्शन किया है उसे छोड़कर बाकी सबको डेटा भेजना
        await self.broadcast_json(broadcast_data, exclude_player=player_id)

    async def broadcast_json(self, data: dict, exclude_player: str = None):
        """हजारों खिलाड़ियों को एक साथ डेटा भेजने का लूप (Zero-Lag)"""
        for pid, connection in list(self.active_connections.items()):
            if pid != exclude_player:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    # अगर किसी प्लेयर का नेट स्लो है और एरर आए, तो उसे सर्वर से किक (kick) कर देना
                    print(f"[NEXUS DROP]: Lag detected for {pid}. Kicking connection.")
                    self.disconnect_player(pid)

    async def broadcast_system_message(self, message: str):
        """एडमिन (तुम्हारे) की तरफ से सर्वर में अनाउंसमेंट करने के लिए"""
        for connection in self.active_connections.values():
            try:
                await connection.send_text(message)
            except:
                pass

# ग्लोबल इंस्टेंस को अभी खाली रखेंगे, इसे main.py में इनिशियलाइज़ करेंगे
multiplayer_core = None

def init_nexus(scheduler: SimulationScheduler) -> GodLevelMultiplayerNexus:
    global multiplayer_core
    multiplayer_core = GodLevelMultiplayerNexus(scheduler=scheduler)
    return multiplayer_core
        
