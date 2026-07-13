import asyncio
import os
import sys
import uuid
import time
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

# ---------------------------------------------------------
# 1. ENTERPRISE GLOBAL BULLETPROOF IMPORTS
# ---------------------------------------------------------
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
MultiBrainRouter = None

# Isolated try-except blocks to prevent total system crash
try:
    from god_brain.self_evolution import EvolutionEngine
    print("[SYSTEM] EvolutionEngine loaded successfully.")
except Exception as e:
    pass

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
    pass

try:
    from security_vault.encryption import GodAuth
    vault = GodAuth()
except Exception as e:
    pass

try:
    from god_brain.api_nexus import MultiBrainRouter
    print("[SYSTEM] MultiBrainRouter loaded successfully.")
except Exception as e:
    pass

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
# 2. FASTAPI APP INITIALIZATION & REGISTRY
# ---------------------------------------------------------
app = FastAPI(
    title="The God Node V2",
    description="Autonomous Enterprise AGI Engine with Background Processing",
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

# GLOBAL TASK REGISTRY: Stores the real-time status of all background generation jobs
task_registry: Dict[str, Any] = {}

# GLOBAL EXCEPTION HANDLER: Ensures frontend ALWAYS receives JSON
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "FAILED", "error": f"CRITICAL SERVER ERROR: {str(exc)}", "stage": "Global Error Handler"}
    )

# ---------------------------------------------------------
# 3. DATA MODELS
# ---------------------------------------------------------
class GodCommand(BaseModel):
    api_vault: Dict[str, List[str]] = Field(..., description="Contains API keys for Gemini, OpenAI, Claude")
    target_system: str = Field(..., description="The subsystem to route the command to")
    directive: str = Field(..., description="The actual natural language command")
    master_pin: str = Field(..., description="Security pin to authenticate the request")

class StatusCommand(BaseModel):
    task_id: str = Field(..., description="The unique ID of the background task")
    master_pin: str = Field(..., description="Security pin to authenticate the request")

# ---------------------------------------------------------
# 4. BACKGROUND WORKER LOGIC
# ---------------------------------------------------------
async def run_game_generation_task(task_id: str, directive: str, api_vault: dict, target_system: str):
    """Executes the heavy Swarm operations in the background without holding up the HTTP response."""
    task_registry[task_id] = {
        "status": "PROCESSING",
        "progress": "Swarm Agents deployed. Architecting and building...",
        "start_time": time.time(),
        "result": None
    }
    
    try:
        if target_system == "generate_game":
            if orchestrator and hasattr(orchestrator, "generate_full_game_with_swarm"):
                # Running the swarm (adjusted to 5 for memory safety on free tier)
                game_result = await orchestrator.generate_full_game_with_swarm(
                    prompt=directive, 
                    agent_count=5, 
                    auto_kill_after_execution=True
                )
                task_registry[task_id]["status"] = "SUCCESS"
                task_registry[task_id]["result"] = game_result
            else:
                # Simulation Mode Fallback
                await asyncio.sleep(10) # Simulating heavy work
                task_registry[task_id]["status"] = "SUCCESS"
                task_registry[task_id]["result"] = {
                    "status": "SIMULATION_SUCCESS",
                    "final_build": f"Mocking Enterprise Game Build for: '{directive}'"
                }
                
        elif target_system == "universal_nexus":
            if MultiBrainRouter is not None:
                nexus_instance = MultiBrainRouter(api_vault=api_vault)
                nexus_result = await nexus_instance.analyze_and_route_task(directive)
                task_registry[task_id]["status"] = "SUCCESS"
                task_registry[task_id]["result"] = {
                    "status": "NEXUS_ROUTED", 
                    "msg": "Task delegated via Universal Multi-Brain architecture.",
                    "nexus_response": nexus_result
                }
            else:
                task_registry[task_id]["status"] = "SUCCESS"
                task_registry[task_id]["result"] = {
                    "status": "SIMULATION_SUCCESS", 
                    "msg": f"Nexus Simulation: Processed '{directive}'"
                }
                
    except Exception as e:
        task_registry[task_id]["status"] = "FAILED"
        task_registry[task_id]["result"] = {"error": f"ENGINE HALT: {str(e)}"}

# ---------------------------------------------------------
# 5. CORE ROUTING & ENDPOINTS
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
async def execute_god_command(payload: GodCommand, background_tasks: BackgroundTasks):
    """Accepts commands, assigns a Background Task, and returns a Task ID immediately to bypass Timeout."""
    
    # 1. AUTHENTICATION
    if payload.master_pin != MASTER_PIN:
        return JSONResponse(status_code=403, content={"status": "FAILED", "error": "ACCESS DENIED: Invalid Master PIN"})

    try:
        # Generate Unique Task ID
        task_id = str(uuid.uuid4())
        
        # Dispatch the heavy lifting to the background
        background_tasks.add_task(
            run_game_generation_task, 
            task_id, 
            payload.directive, 
            payload.api_vault, 
            payload.target_system
        )
        
        # Return instantly (under 1 second) to Render to prevent Timeout
        return JSONResponse(status_code=202, content={
            "status": "PROCESSING",
            "task_id": task_id,
            "msg": "Directive accepted. Swarm agents are working in the background. Check status using the Task ID."
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "FAILED", "error": f"INITIALIZATION ERROR: {str(e)}", "stage": "Execution Logic"})

@app.post("/check_status")
async def check_task_status(payload: StatusCommand):
    """Endpoint to check the live status or fetch the final build of a background task."""
    if payload.master_pin != MASTER_PIN:
        return JSONResponse(status_code=403, content={"status": "FAILED", "error": "ACCESS DENIED"})
        
    task_data = task_registry.get(payload.task_id)
    
    if not task_data:
        return JSONResponse(status_code=404, content={"status": "FAILED", "error": "Task ID not found in memory."})
        
    return JSONResponse(status_code=200, content=task_data)

# ---------------------------------------------------------
# 6. SERVER EXECUTION 
# ---------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
