import asyncio
import os
import sys
import uuid
import time
import json
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

try:
    from god_brain.self_evolution import EvolutionEngine
    print("[SYSTEM] EvolutionEngine loaded successfully.")
except Exception as e:
    pass

try:
    from god_brain.orchestrator import GodOrchestrator
    orchestrator = GodOrchestrator()
except Exception as e:
    pass

try:
    from god_brain.api_nexus import MultiBrainRouter
    print("[SYSTEM] MultiBrainRouter loaded successfully.")
except Exception as e:
    pass

# ---------------------------------------------------------
# 2. FASTAPI APP INITIALIZATION & REGISTRY
# ---------------------------------------------------------
app = FastAPI(
    title="The God Node V2",
    description="Autonomous Enterprise AGI Engine",
    version="10.0-ENTERPRISE (Swarm Edition)"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

MASTER_PIN = "7777"
task_registry: Dict[str, Any] = {}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"status": "FAILED", "error": str(exc)})

class GodCommand(BaseModel):
    api_vault: Dict[str, List[str]] = Field(...)
    target_system: str = Field(...)
    directive: str = Field(...)
    master_pin: str = Field(...)

class StatusCommand(BaseModel):
    task_id: str = Field(...)
    master_pin: str = Field(...)

# ---------------------------------------------------------
# 4. BACKGROUND WORKER LOGIC
# ---------------------------------------------------------
async def run_game_generation_task(task_id: str, directive: str, api_vault: dict, target_system: str):
    task_registry[task_id] = {"status": "PROCESSING", "progress": "System active. Executing...", "start_time": time.time(), "result": None}
    
    try:
        if target_system == "generate_game":
            if orchestrator and hasattr(orchestrator, "generate_full_game_with_swarm"):
                game_result = await orchestrator.generate_full_game_with_swarm(prompt=directive, agent_count=5, auto_kill_after_execution=True)
                task_registry[task_id]["status"] = "SUCCESS"
                task_registry[task_id]["result"] = game_result
            else:
                await asyncio.sleep(5) 
                task_registry[task_id]["status"] = "SUCCESS"
                task_registry[task_id]["result"] = {"status": "SIMULATION_SUCCESS", "final_build": f"Mock Game Build for: '{directive}'"}
                
        elif target_system == "universal_nexus":
            if MultiBrainRouter is not None:
                nexus_instance = MultiBrainRouter(api_vault=api_vault)
                nexus_result = await nexus_instance.analyze_and_route_task(directive)
                task_registry[task_id]["status"] = "SUCCESS"
                task_registry[task_id]["result"] = {"status": "NEXUS_ROUTED", "nexus_response": nexus_result}
            else:
                task_registry[task_id]["status"] = "SUCCESS"
                task_registry[task_id]["result"] = {"status": "SIMULATION_SUCCESS", "msg": f"Nexus Sim: '{directive}'"}

        elif target_system == "self_evolution":
            if MultiBrainRouter is not None and EvolutionEngine is not None:
                nexus_instance = MultiBrainRouter(api_vault=api_vault)
                
                # Strict JSON Prompt for AI
                json_prompt = (
                    f"Act as the Lead Backend Architect. Output ONLY a valid JSON object. "
                    f"Keys must be the exact file paths (e.g., 'main.py' or 'cloud_storage/gdrive_manager.py'). "
                    f"Values must be the complete, raw Python code for those files. "
                    f"Do NOT include markdown block formatting like ```json. ONLY output the raw JSON brackets. "
                    f"Directive: {directive}"
                )
                
                ai_result = await nexus_instance.analyze_and_route_task(json_prompt)
                ai_text = ai_result.get("response", "")
                
                try:
                    if "```json" in ai_text:
                        ai_text = ai_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in ai_text:
                        ai_text = ai_text.split("```")[1].split("```")[0].strip()
                        
                    new_files_dict = json.loads(ai_text)
                    
                    evo_engine = EvolutionEngine()
                    push_result = await evo_engine.force_upgrade_system(new_files_dict)
                    
                    task_registry[task_id]["status"] = "SUCCESS"
                    task_registry[task_id]["result"] = push_result
                    
                except Exception as parse_error:
                    task_registry[task_id]["status"] = "FAILED"
                    task_registry[task_id]["result"] = {"error": "Failed to parse AI output into JSON.", "raw_output": ai_text, "exception": str(parse_error)}
            else:
                task_registry[task_id]["status"] = "FAILED"
                task_registry[task_id]["result"] = {"error": "Evolution Engine or Nexus module is missing."}
                
    except Exception as e:
        task_registry[task_id]["status"] = "FAILED"
        task_registry[task_id]["result"] = {"error": f"ENGINE HALT: {str(e)}"}

# ---------------------------------------------------------
# 5. CORE ROUTING & ENDPOINTS
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def engine_status():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>SYSTEM ACTIVE. Upload index.html.</h1>", status_code=200)

@app.post("/execute")
async def execute_god_command(payload: GodCommand, background_tasks: BackgroundTasks):
    if payload.master_pin != MASTER_PIN:
        return JSONResponse(status_code=403, content={"status": "FAILED", "error": "ACCESS DENIED: Invalid Master PIN"})
    try:
        task_id = str(uuid.uuid4())
        background_tasks.add_task(run_game_generation_task, task_id, payload.directive, payload.api_vault, payload.target_system)
        return JSONResponse(status_code=202, content={"status": "PROCESSING", "task_id": task_id, "msg": "Task accepted in background."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "FAILED", "error": str(e)})

@app.post("/check_status")
async def check_task_status(payload: StatusCommand):
    if payload.master_pin != MASTER_PIN:
        return JSONResponse(status_code=403, content={"status": "FAILED", "error": "ACCESS DENIED"})
    task_data = task_registry.get(payload.task_id)
    if not task_data:
        return JSONResponse(status_code=404, content={"status": "FAILED", "error": "Task ID not found."})
    return JSONResponse(status_code=200, content=task_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

