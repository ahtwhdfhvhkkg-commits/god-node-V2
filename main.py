import asyncio
import os
import sys
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

# ---------------------------------------------------------
# 1. ENTERPRISE-GRADE BULLETPROOF IMPORTS
# ---------------------------------------------------------
# Initializing global instances to None to prevent NameError
EvolutionEngine = None
orchestrator = None
gateway = None
vault = None
cpp_engine = None
multiplayer_nexus = None
asset_forge = None
economy = None
s3_cloud = None
pixel_stream = None
deployment = None

# We use isolated try-except blocks for EACH import. 
# This ensures that one missing or empty file does not crash the entire neural network.

try:
    from god_brain.self_evolution import EvolutionEngine
    print("[SYSTEM] EvolutionEngine loaded successfully.")
except Exception as e:
    print(f"[WARNING] EvolutionEngine import failed: {e}")

try:
    from god_brain.orchestrator import GodOrchestrator
    orchestrator = GodOrchestrator()
    print("[SYSTEM] GodOrchestrator loaded successfully.")
except Exception as e:
    print(f"[WARNING] GodOrchestrator import failed: {e}")

try:
    from core.gateway import GatewayRouter
    gateway = GatewayRouter()
except Exception as e:
    print(f"[WARNING] GatewayRouter import failed: {e}")

try:
    from security_vault.encryption import GodAuth
    vault = GodAuth()
except Exception as e:
    print(f"[WARNING] GodAuth import failed: {e}")

try:
    from core_engine.cpp_bridge import CPPExecutionBridge
    cpp_engine = CPPExecutionBridge()
except Exception as e:
    pass

try:
    from multiplayer_nexus.sync_server import GodLevelMultiplayerNexus
    multiplayer_nexus = GodLevelMultiplayerNexus()
except Exception as e:
    pass

try:
    from assets_factory.asset_manager import GodAssetForge
    asset_forge = GodAssetForge()
except Exception as e:
    pass

try:
    from economy_vault.billing_core import GodEconomyEngine
    economy = GodEconomyEngine()
except Exception as e:
    pass

try:
    from cloud_storage.s3_manager import S3CloudManager
    s3_cloud = S3CloudManager()
except Exception as e:
    pass

try:
    from pixel_streaming.webrtc_core import PixelStreamEngine
    pixel_stream = PixelStreamEngine()
except Exception as e:
    pass

try:
    from deployment.deployment_core import GodDeploymentManager
    deployment = GodDeploymentManager()
except Exception as e:
    pass


# ---------------------------------------------------------
# 2. FASTAPI APP INITIALIZATION
# ---------------------------------------------------------
app = FastAPI(
    title="The God Node V2",
    description="Autonomous Enterprise AGI Engine",
    version="10.0-ENTERPRISE (Swarm Edition)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MASTER_PIN = "7777"

# ---------------------------------------------------------
# 3. DATA MODELS
# ---------------------------------------------------------
class GodCommand(BaseModel):
    api_vault: Dict[str, List[str]] = Field(..., description="Contains API keys for Gemini, OpenAI, Claude")
    target_system: str = Field(..., description="The subsystem to route the command to")
    directive: str = Field(..., description="The actual natural language command")
    master_pin: str = Field(..., description="Security pin to authenticate the request")


# ---------------------------------------------------------
# 4. CORE ROUTING & ENDPOINTS
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def engine_status():
    """Serves the frontend Command Center UI."""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1 style='color: #00ffcc; background: #0a0a0f; padding: 20px; font-family: monospace;'>SYSTEM ACTIVE. Upload index.html to view UI.</h1>",
            status_code=200
        )

@app.post("/execute")
async def execute_god_command(payload: GodCommand):
    """The Master API Endpoint that routes commands to the appropriate AI Brain."""
    
    # 1. AUTHENTICATION
    if payload.master_pin != MASTER_PIN:
        raise HTTPException(status_code=403, detail="ACCESS DENIED: Invalid Master PIN")

    try:
        # ---------------------------------------------------------
        # PATH 1: GAME GENERATION (ORCHESTRATOR SWARM)
        # ---------------------------------------------------------
        if payload.target_system == "generate_game":
            if orchestrator and hasattr(orchestrator, "generate_full_game_with_swarm"):
                # We have the real orchestrator loaded
                game_result = await orchestrator.generate_full_game_with_swarm(
                    prompt=payload.directive, 
                    agent_count=200, 
                    auto_kill_after_execution=True
                )
                return game_result
            else:
                # Simulation mode if orchestrator is missing
                return {
                    "status": "SIMULATION_SUCCESS",
                    "final_build": f"Mocking Enterprise Game Build for: '{payload.directive}'"
    }
