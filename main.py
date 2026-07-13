import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any

# ---------------------------------------------------------
# 1. THE MASTER LINK
# ---------------------------------------------------------
try:
    from core.gateway import GatewayRouter
    from god_brain.self_evolution import EvolutionEngine
    from core_engine.cpp_bridge import CPPExecutionBridge
    from security_vault.encryption import GodAuth
    from multiplayer_nexus.sync_server import GodLevelMultiplayerNexus
    from assets_factory.asset_manager import GodAssetForge
    from economy_vault.billing_core import GodEconomyEngine
    
    from god_brain.orchestrator import GodOrchestrator
    from cloud_storage.s3_manager import S3CloudManager
    from pixel_streaming.webrtc_core import PixelStreamEngine
    from deployment.deployment_core import GodDeploymentManager
except ImportError as e:
    print(f"CRITICAL IMPORT WARNING: {e}")

app = FastAPI(title="The God Node V2", version="10.0-ENTERPRISE (Swarm Edition)")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# ---------------------------------------------------------
# 2. FULL SYSTEM INITIALIZATION
# ---------------------------------------------------------
vault = cpp_engine = multiplayer_nexus = asset_forge = economy = None
orchestrator = s3_cloud = pixel_stream = deployment = None

try:
    vault = GodAuth()
    cpp_engine = CPPExecutionBridge()
    multiplayer_nexus = GodLevelMultiplayerNexus()
    asset_forge = GodAssetForge()
    economy = GodEconomyEngine()
    orchestrator = GodOrchestrator()
    s3_cloud = S3CloudManager()
    pixel_stream = PixelStreamEngine()
    deployment = GodDeploymentManager()
except NameError:
    pass 

MASTER_PIN = "7777"

class GodCommand(BaseModel):
    api_vault: Dict[str, List[str]] = Field(...)
    target_system: str = Field(...)
    directive: str = Field(...)
    master_pin: str = Field(...)

# ---------------------------------------------------------
# 3. COMMAND CENTER ROUTER
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def engine_status():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>SYSTEM ACTIVE. Upload index.html</h1>", status_code=200)

@app.post("/execute")
async def execute_god_command(payload: GodCommand):
    if payload.master_pin != MASTER_PIN:
        raise HTTPException(status_code=403, detail="ACCESS DENIED: Invalid Master PIN")

    try:
        if payload.target_system == "generate_game":
            if orchestrator and hasattr(orchestrator, "generate_full_game_with_swarm"):
                game_result = await orchestrator.generate_full_game_with_swarm(
                    prompt=payload.directive, agent_count=200, auto_kill_after_execution=True
                )
            else:
                game_result = {
                    "status": "SIMULATION_SUCCESS", 
                    "final_build": f"Mocking GTA Game for prompt: '{payload.directive}'. (Orchestrator module missing!)"
                }
            return game_result
        
        elif payload.target_system == "self_update":
            # ---------------------------------------------------------
            # THE REAL UPGRADER (SELF-EVOLUTION) UNLOCKED
            # ---------------------------------------------------------
            api_keys = payload.api_vault.get("gemini", [])
            if not api_keys or not api_keys[0]:
                return {"status": "ERROR", "msg": "CRITICAL: Gemini API Key missing in Vault!"}
            
            try:
                # सीधे तुम्हारे सेल्फ-अपग्रेडर (EvolutionEngine) को कमांड जा रही है
                evolution = EvolutionEngine(api_gateway={"gemini": api_keys[0]})
                result = await evolution.evolve_file("index.html", payload.directive)
                
                return {
                    "status": "EVOLUTION_SUCCESS", 
                    "msg": "The AI Agent has successfully modified the code!",
                    "details": result
                }
            except Exception as e:
                # अगर कोई भी एरर आया तो सर्वर क्रैश नहीं होगा, बल्कि एरर मैसेज दिखा देगा
                return {"status": "ERROR", "msg": f"Evolution failed: {str(e)}"}

        else:
            return {"status": "Gateway Routing Active", "msg": f"Routed to {payload.target_system}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ENGINE HALT: str({e})")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
        
