import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any

# =====================================================================
# 1. THE MASTER LINK: तुम्हारी पूरी 25+ फाइलों की सेना यहाँ जुड़ रही है
# =====================================================================
try:
    from core.gateway import GatewayResolver
    from god_brain.self_evolution import EvolutionEngine
    from core_engine.cpp_bridge import CPPExecutionBridge
    from security_vault.encryption import GodVault
    from multiplayer_nexus.sync_server import GodLevelMultiplayerNexus
    from assets_factory.asset_manager import GodAssetForge
    from economy_vault.billing_core import GodEconomyEngine
    
    # द गॉड नोड V2 (New Enterprise Modules)
    from god_brain.orchestrator import GodOrchestrator
    from cloud_storage.s3_manager import S3CloudManager
    from pixel_streaming.webrtc_core import PixelStreamEngine
    from deployment.deployment_core import GodDeploymentManager
except ImportError as e:
    raise RuntimeError(f"CRITICAL IMPORT ERROR: {e}. सारे फोल्डर्स और फाइलें चेक करें!")

# =====================================================================
# 2. गॉड नोड इनिशियलाइज़ेशन (सिस्टम बूट-अप)
# =====================================================================
app = FastAPI(title="The God Node V2", version="20.0-ENTERPRISE (Unreal Killer)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# सारे इंजन्स को मेमोरी (RAM) में लोड करना
vault = GodVault()
cpp_engine = CPPExecutionBridge()
multiplayer_nexus = GodLevelMultiplayerNexus()
asset_forge = GodAssetForge()
economy = GodEconomyEngine()

orchestrator = GodOrchestrator()
s3_cloud = S3CloudManager()
pixel_stream = PixelStreamEngine()
deployment = GodDeploymentManager()

MASTER_PIN = "7777"

# =====================================================================
# 3. मल्टी-एपीआई डेटा स्ट्रक्चर्स
# =====================================================================
class GodCommand(BaseModel):
    api_vault: Dict[str, List[str]] = Field(..., description="Multi-API Key Vault")
    target_system: str = Field(..., description="Options: pure_ai, self_update, cpp_render, generate_game")
    directive: str = Field(..., description="The prompt or command")
    master_pin: str = Field(..., description="Security PIN")

class DeploymentCommand(BaseModel):
    game_id: str
    player_id: str = None
    action: str = None # ban or unban
    master_pin: str

# =====================================================================
# 4. द नर्वस सिस्टम (API एंडपॉइंट्स)
# =====================================================================
@app.get("/")
async def engine_status():
    """सिस्टम हेल्थ चेक"""
    return {"status": "GOD NODE V2 ONLINE", "systems": "100% MULTI-AGENT SYNCED"}

@app.post("/execute")
async def execute_god_command(payload: GodCommand):
    """द मास्टर राउट: तुम्हारे फोन से आने वाले सारे कमांड्स यहीं प्रोसेस होंगे"""
    if payload.master_pin != MASTER_PIN:
        raise HTTPException(status_code=403, detail="ACCESS DENIED: Invalid Master PIN")
    
    try:
        # 25,000 लिमिट वाला लोड बैलेंसर एक्टिवेट करना
        GatewayResolver.load_vault(payload.api_vault)
        
        # अगर कमांड "पूरा गेम बनाने" का है (The Orchestrator)
        if payload.target_system == "generate_game":
            game_result = orchestrator.generate_full_game(payload.directive)
            
            if game_result["status"] == "SUCCESS":
                # गेम बनते ही उसे सीधे टेस्टर रूम (Staging) में भेज देना
                staging_info = deployment.push_to_staging(
                    game_id="game_" + payload.directive[:5].replace(" ", "_"), 
                    game_data=game_result["final_build"]
                )
                return {"game_status": "BUILT", "deployment": staging_info}
            return game_result

        # अगर कमांड सेल्फ-अपडेट का है
        elif payload.target_system == "self_update":
            ai_gateway = GatewayResolver.get_gateway("brain")
            evolution = EvolutionEngine(ai_gateway=ai_gateway)
            return evolution.evolve_file("main.py", payload.directive)
            
        else:
            # नार्मल AI चैट या बेसिक कमांड्स
            ai_gateway = GatewayResolver.get_gateway("brain")
            return {"response": ai_gateway.generate(payload.directive)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ENGINE HALT: {str(e)}")

# =====================================================================
# 5. गॉड पैनल (डिप्लॉयमेंट और लाइव कंट्रोल)
# =====================================================================
@app.post("/deploy/live")
async def go_live(payload: DeploymentCommand):
    """स्टैजिंग से गेम को अप्रूव करके दुनिया के लिए लाइव करना"""
    return deployment.approve_and_go_live(payload.game_id, payload.master_pin)

@app.post("/deploy/access")
async def manage_player_access(payload: DeploymentCommand):
    """किसी भी प्लेयर को बैन (Ban) या अनबैन करना"""
    return deployment.manage_access(payload.game_id, payload.player_id, payload.action, payload.master_pin)

# =====================================================================
# 6. पिक्सल स्ट्रीमिंग और मल्टीप्लेयर नेक्सस (Zero-Latency WebSockets)
# =====================================================================
@app.websocket("/multiplayer/{player_id}")
async def multiplayer_connection(websocket: WebSocket, player_id: str):
    await multiplayer_nexus.connect_player(player_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await multiplayer_nexus.process_action(player_id, data)
    except WebSocketDisconnect:
        multiplayer_nexus.disconnect_player(player_id)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

