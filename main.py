"""
main.py
ENTERPRISE EDITION: God Node V2 Master Server (2040 Architecture)

The Ultimate Central Nervous System.
Wires together AI Swarms, C++ Simulation, WebRTC, Multi-Agent Routing,
Self-Evolution, and Quantum Reality Engines.
"""

import asyncio
import os
import uuid
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

# =====================================================================
# 1. ENTERPRISE LOGGING
# =====================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [GOD NODE CORE] - %(levelname)s - %(message)s')
logger = logging.getLogger("GodNode.Main")

# =====================================================================
# 2. GLOBAL SYSTEM REGISTRY (The Backbone)
# =====================================================================
SYSTEM_REGISTRY = {}

# A. Security & Economy
try:
    from security_vault.encryption import GodAuth
    SYSTEM_REGISTRY["vault"] = GodAuth()
    logger.info("✅ Security Vault ONLINE.")
except Exception as e:
    logger.critical(f"❌ Security Vault failed: {e}")

try:
    from economy_vault.billing_core import GodEconomyEngine
    SYSTEM_REGISTRY["economy"] = GodEconomyEngine()
    logger.info("✅ Economy Engine ONLINE.")
except Exception as e:
    logger.warning(f"⚠️ Economy Engine failed: {e}")

# B. Database & Cloud
try:
    from cloud_storage.db_manager import db_vault
    SYSTEM_REGISTRY["db_cloud"] = db_vault
    logger.info("✅ Async Cloud Database ONLINE.")
except Exception as e:
    logger.warning(f"⚠️ Cloud DB failed: {e}")

# C. The Brains (Routers, Gateways, Connection Pools, Orchestrator)
try:
    from god_brain.connection_pool import HTTP_CLIENT
    SYSTEM_REGISTRY["connection_pool"] = HTTP_CLIENT
    logger.info("✅ HTTP Connection Pool ONLINE.")
except Exception as e:
    logger.critical(f"❌ HTTP Connection Pool failed: {e}")

try:
    from core.gateway import GatewayRouter
    gateway_instance = GatewayRouter()
    SYSTEM_REGISTRY["gateway"] = gateway_instance
    logger.info("✅ API Gateway (Load Balancer) ONLINE.")
except Exception as e:
    logger.critical(f"❌ API Gateway failed: {e}")

try:
    from the_god_router.intent_classifier import master_router_instance
    SYSTEM_REGISTRY["master_router"] = master_router_instance
    logger.info("✅ Master Intent Router ONLINE.")
except Exception as e:
    logger.critical(f"❌ Master Router failed: {e}")

try:
    from god_brain.orchestrator import GodOrchestrator
    SYSTEM_REGISTRY["orchestrator"] = GodOrchestrator()
    logger.info("✅ God Orchestrator (AI Swarm Manager) ONLINE.")
except Exception as e:
    logger.critical(f"❌ God Orchestrator failed: {e}")

# D. The Engine (Scheduler, C++ Bridge, Multiplayer Nexus, ODRE)
try:
    from simulation_scheduler.config import SchedulerConfig
    from simulation_scheduler.scheduler import SimulationScheduler
    from core_engine.cpp_bridge import SimulationCPPAdapter
    from multiplayer_nexus.sync_server import init_nexus

    engine_config = SchedulerConfig()
    master_scheduler = SimulationScheduler(engine_config)
    SYSTEM_REGISTRY["scheduler"] = master_scheduler

    cpp_adapter = SimulationCPPAdapter(workspace_dir="workspace_cpp")
    SYSTEM_REGISTRY["cpp_bridge"] = cpp_adapter

    nexus = init_nexus(master_scheduler)
    SYSTEM_REGISTRY["nexus"] = nexus
    logger.info("✅ C++ Simulation Engine & 30k-Player Nexus ONLINE.")
except Exception as e:
    logger.critical(f"❌ Core Game Engine failed: {e}")

try:
    from core_engine.odre_core import reality_core
    SYSTEM_REGISTRY["odre_engine"] = reality_core
    logger.info("✅ ODRE (Observer-Dependent Reality Engine) ONLINE.")
except Exception as e:
    logger.critical(f"❌ ODRE Engine failed: {e}")

try:
    from assets_factory.world_builder import world_forge
    SYSTEM_REGISTRY["world_forge"] = world_forge
    logger.info("✅ Procedural World Builder (Assets Factory) ONLINE.")
except Exception as e:
    logger.warning(f"⚠️ Assets Factory failed: {e}")

# E. Compilers, Streaming & Live Editing
try:
    from pixel_streaming.stream_manager import PixelStreamEngine
    SYSTEM_REGISTRY["pixel_stream"] = PixelStreamEngine()
    logger.info("✅ WebRTC Pixel Streaming ONLINE.")
except Exception as e:
    logger.warning(f"⚠️ Pixel Streaming failed: {e}")

try:
    from live_editor.hot_reloader import vibe_coder_engine
    SYSTEM_REGISTRY["hot_reloader"] = vibe_coder_engine
    logger.info("✅ CRDT Hot-Reloader (Vibe Coding) ONLINE.")
except Exception as e:
    logger.warning(f"⚠️ Hot-Reloader failed: {e}")

try:
    from game_compilers.universal_builder import game_builder
    SYSTEM_REGISTRY["builder"] = game_builder
    logger.info("✅ Universal Game Compiler (ZIP/APK/EXE) ONLINE.")
except Exception as e:
    logger.warning(f"⚠️ Universal Builder failed: {e}")

try:
    from god_brain.self_evolution import EvolutionEngine
    SYSTEM_REGISTRY["evolution"] = EvolutionEngine()
    logger.info("✅ Autonomous Self-Evolution Engine ONLINE.")
except Exception as e:
    logger.warning(f"⚠️ Self-Evolution Engine failed: {e}")


# =====================================================================
# 3. GAME LOOP & LIFESPAN (60Hz Engine Tick)
# =====================================================================
async def engine_tick_loop():
    """Pulls tasks from the Priority Queue and executes them in C++ at 60Hz."""
    logger.info("⚙️ Master Engine Tick Loop Activated (60Hz)...")
    scheduler = SYSTEM_REGISTRY.get("scheduler")
    cpp_bridge = SYSTEM_REGISTRY.get("cpp_bridge")

    if not scheduler or not cpp_bridge:
        logger.error("Tick Loop Halted: Scheduler or C++ Bridge missing.")
        return

    while True:
        try:
            batches = scheduler.build_batches()
            for batch in batches:
                # Execution layer processing
                cpp_bridge.execute(batch)
        except Exception as e:
            logger.error(f"Engine Tick Error: {e}")
        
        await asyncio.sleep(0.016) # ~60 FPS

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events cleanly."""
    logger.info("🚀 GOD NODE V2 BOOT SEQUENCE INITIATED...")
    
    if SYSTEM_REGISTRY.get("connection_pool"):
        await SYSTEM_REGISTRY["connection_pool"].startup()
    
    loop_task = asyncio.create_task(engine_tick_loop())
    yield 
    
    logger.info("🛑 GOD NODE V2 SHUTDOWN SEQUENCE INITIATED...")
    loop_task.cancel()
    if SYSTEM_REGISTRY.get("connection_pool"):
        await SYSTEM_REGISTRY["connection_pool"].shutdown()

# =====================================================================
# 4. FASTAPI INITIALIZATION
# =====================================================================
app = FastAPI(title="God Node V2", version="10.0-ENTERPRISE", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Connect the Gateway Router to FastAPI (Fix for previous missing connection)
if SYSTEM_REGISTRY.get("gateway"):
    app.include_router(SYSTEM_REGISTRY["gateway"].get_router())

MASTER_PIN = os.getenv("GOD_MASTER_PIN", "7777")
active_tasks_registry: Dict[str, Any] = {}

# =====================================================================
# 5. SCHEMAS (Pydantic)
# =====================================================================
class GodCommandPayload(BaseModel):
    directive: str = Field(..., description="The user's raw prompt.")
    master_pin: str = Field(...)
    context_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class BuildExportPayload(BaseModel):
    game_id: str = Field(...)
    target_platform: str = Field(pattern="^(web|mobile|pc)$")
    master_pin: str = Field(...)

class WebRTCOfferPayload(BaseModel):
    player_id: str = Field(...)
    sdp: str = Field(...)
    type: str = Field(...)

# =====================================================================
# 6. BACKGROUND ORCHESTRATION PIPELINE
# =====================================================================
async def process_god_command_task(task_id: str, directive: str):
    """The Full Pipeline: Routing -> Swarm Orchestration -> QA -> Output"""
    active_tasks_registry[task_id] = {"status": "ANALYZING", "progress": 10, "result": None}
    
    router = SYSTEM_REGISTRY.get("master_router")
    orchestrator = SYSTEM_REGISTRY.get("orchestrator")
    
    try:
        # STEP 1: Routing & Resource Allocation
        if not router: raise RuntimeError("Master Router offline.")
        routing_plan = await router.analyze_and_allocate(directive)
        active_tasks_registry[task_id]["progress"] = 30
        active_tasks_registry[task_id]["status"] = "ORCHESTRATING_SWARM"

        # STEP 2: Swarm Execution (Generates Assets, Map, Physics, QA Tests)
        if not orchestrator: raise RuntimeError("Orchestrator offline.")
        
        target_platform = routing_plan.get("architecture", {}).get("target_platform", "web_html5")
        agent_count = 10 if target_platform != "web_html5" else 5 # Scale agents based on platform
        
        swarm_result = await orchestrator.generate_full_game_with_swarm(
            prompt=directive, 
            agent_count=agent_count
        )
        active_tasks_registry[task_id]["progress"] = 90
        
        if swarm_result.get("status") == "FAILED":
            raise RuntimeError(swarm_result.get("error", "Swarm execution failed."))

        # STEP 3: Finalize
        active_tasks_registry[task_id]["status"] = "SUCCESS"
        active_tasks_registry[task_id]["progress"] = 100
        active_tasks_registry[task_id]["result"] = {
            "routing_plan": routing_plan,
            "final_build": swarm_result.get("final_build")
        }
        
    except Exception as e:
        logger.error(f"Task {task_id} Failed: {str(e)}")
        active_tasks_registry[task_id]["status"] = "FAILED"
        active_tasks_registry[task_id]["result"] = {"error": str(e)}

# =====================================================================
# 7. REST ENDPOINTS
# =====================================================================
@app.get("/", response_class=HTMLResponse)
async def serve_control_panel():
    """Serves the High-Tech God Node Control Panel UI."""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>God Node Active. index.html missing.</h1>", status_code=200)

@app.post("/api/v2/execute")
async def execute_command(payload: GodCommandPayload, bg_tasks: BackgroundTasks):
    """Primary entry point for user prompts."""
    if payload.master_pin != MASTER_PIN:
        raise HTTPException(status_code=403, detail="ACCESS DENIED")
    
    task_id = f"TASK_{uuid.uuid4().hex[:8]}"
    bg_tasks.add_task(process_god_command_task, task_id, payload.directive)
    return JSONResponse(status_code=202, content={"status": "PROCESSING", "task_id": task_id})

@app.get("/api/v2/status/{task_id}")
async def check_status(task_id: str):
    """Poll endpoint for the UI to check generation progress."""
    task = active_tasks_registry.get(task_id)
    if not task: 
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(status_code=200, content=task)

@app.post("/api/v2/export")
async def trigger_universal_build(payload: BuildExportPayload):
    """Triggers the game_compilers/universal_builder.py to create ZIP/APK/EXE."""
    if payload.master_pin != MASTER_PIN:
        raise HTTPException(status_code=403, detail="ACCESS DENIED")
    
    builder = SYSTEM_REGISTRY.get("builder")
    if not builder: 
        raise HTTPException(status_code=500, detail="Universal Builder offline.")
    
    # In a real environment, pull the exact code from DB Vault
    mock_config = {
        "game_id": payload.game_id,
        "target_platform": payload.target_platform,
        "html_content": "<!-- Compiled by God Node -->\n<canvas></canvas>",
        "js_content": "console.log('Game Initialized');"
    }
    result = await builder.build_game(mock_config)
    return JSONResponse(status_code=200, content=result)

@app.post("/api/v2/evolve")
async def trigger_self_evolution(pin: str):
    """Triggers the God Node to scan itself and write missing code."""
    if pin != MASTER_PIN:
        raise HTTPException(status_code=403, detail="ACCESS DENIED")
    
    evolution_engine = SYSTEM_REGISTRY.get("evolution")
    if not evolution_engine:
        raise HTTPException(status_code=500, detail="Evolution Engine Offline.")
        
    result = await evolution_engine.evolve()
    return JSONResponse(status_code=200, content=result)

@app.post("/api/v2/stream/offer")
async def webrtc_handshake(payload: WebRTCOfferPayload):
    """WebRTC SDP Handshake for Pixel Streaming (Cloud Gaming)."""
    stream_engine = SYSTEM_REGISTRY.get("pixel_stream")
    if not stream_engine:
        raise HTTPException(status_code=500, detail="Pixel Stream Engine offline.")
    
    try:
        result = await stream_engine.create_stream_connection(
            player_id=payload.player_id, 
            offer_sdp=payload.sdp, 
            offer_type=payload.type
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"WebRTC Handshake failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================================
# 8. WEBSOCKET ENDPOINTS (REAL-TIME)
# =====================================================================
@app.websocket("/live-edit/{game_id}")
async def ws_vibe_coder(websocket: WebSocket, game_id: str):
    """CRDT-powered Hot Reloader endpoint for Vibe Coding."""
    reloader = SYSTEM_REGISTRY.get("hot_reloader")
    if not reloader:
        await websocket.close(code=1011, reason="Hot Reloader Offline")
        return
        
    await reloader.connection_manager.connect(game_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            logger.debug(f"[HOT-RELOAD] Update: {data}")
    except WebSocketDisconnect:
        reloader.connection_manager.disconnect(game_id)

@app.websocket("/ws/multiplayer/{player_id}")
async def ws_multiplayer_nexus(websocket: WebSocket, player_id: str):
    """Massive 30k-player sync server endpoint (Routes to C++ Scheduler)."""
    nexus = SYSTEM_REGISTRY.get("nexus")
    if not nexus:
        await websocket.close(code=1011, reason="Nexus Offline")
        return
        
    await nexus.connect_player(player_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await nexus.process_action(player_id, data)
    except Exception as e:
        logger.error(f"[NEXUS WS ERROR] Player {player_id}: {e}")
        nexus.disconnect_player(player_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
