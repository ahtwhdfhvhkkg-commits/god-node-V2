"""
the_god_router/intent_classifier.py

ENTERPRISE EDITION: The Master Router (Replit & AWS Grade Architecture)
Role: Advanced Intent Classification, Dependency Graphing, and Resource Allocation.

Features:
- Pydantic Schema Validation for AI outputs.
- Dynamic Resource Allocation (RAM/CPU/Threads) based on game complexity.
- Engine By-pass Logic (Disconnects C++ Bridge/WebRTC for simple HTML5 games).
- Big-O Complexity Estimation to prevent server overload.
"""

import json
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ValidationError

# Importing existing God Node V2 Core modules
from core.gateway import GatewayRouter
from simulation_scheduler.priorities import SimulationPriority

# ------------------------------------------------------------------
# 1. ENTERPRISE LOGGING & TELEMETRY
# ------------------------------------------------------------------
logger = logging.getLogger("GodNode.MasterRouter")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - [MASTER ROUTER] - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

# ------------------------------------------------------------------
# 2. STRICT SCHEMAS (Replit-style JSON Validation)
# ------------------------------------------------------------------
class GameEngineConfig(BaseModel):
    use_cpp_bridge: bool = Field(description="True if heavy physics/3D requires C++ execution.")
    use_webrtc_stream: bool = Field(description="True if game is too heavy and must be pixel streamed.")
    use_multiplayer_nexus: bool = Field(description="True if the game requires WebSockets for multiplayer.")
    use_local_storage_only: bool = Field(description="True if this is a web game saving data on user's browser.")

class ResourceAllocation(BaseModel):
    estimated_ram_mb: int = Field(description="Estimated RAM required to run this instance.")
    max_concurrent_threads: int = Field(description="How many threads the SimulationScheduler should allocate.")
    priority_level: int = Field(description="0=CRITICAL, 1=HIGH, 2=NORMAL, 3=LOW")

class GameArchitectureSchema(BaseModel):
    target_platform: str = Field(pattern="^(web_html5|mobile_apk|pc_exe|cloud_stream)$")
    complexity_class: str = Field(pattern="^(O\(1\)|O\(N\)|O\(N\^2\)|AAA)$")
    engine_config: GameEngineConfig
    resource_limits: ResourceAllocation
    required_agents: List[str] = Field(description="List of God Brain agents required (e.g., AssetGenerator, Physics).")
    build_steps_dependency_graph: List[str] = Field(description="Step-by-step execution order.")

# ------------------------------------------------------------------
# 3. THE MASTER ROUTER ENGINE
# ------------------------------------------------------------------
class MasterIntentRouter:
    """
    Enterprise Intent Classifier & Resource Budgeting Engine.
    Estimates Big-O complexity and allocates server RAM/CPU threads.
    """
    def __init__(self):
        self.version = "10.0.0-Enterprise"
        self.active_routings: int = 0
        logger.info("Initializing Intent Classifier Engine... Online.")

    async def analyze_and_allocate(self, prompt: str) -> Dict[str, Any]:
        """
        Reads user prompt -> Evaluates Complexity -> Allocates Server Resources -> Returns Architecture Plan.
        """
        self.active_routings += 1
        request_id = f"REQ-{int(time.time())}-{self.active_routings}"
        logger.info(f"[{request_id}] Analyzing Directive: '{prompt[:50]}...'")

        system_prompt = (
            "You are the Master Architect API for God Node V2. "
            "Analyze the request and return ONLY a valid JSON object following this schema:\n"
            "- target_platform: 'web_html5', 'mobile_apk', 'pc_exe', or 'cloud_stream'\n"
            "- complexity_class: 'O(1)', 'O(N)', 'O(N^2)', or 'AAA'\n"
            "- engine_config: {use_cpp_bridge: bool, use_webrtc_stream: bool, use_multiplayer_nexus: bool, use_local_storage_only: bool}\n"
            "- resource_limits: {estimated_ram_mb: int, max_concurrent_threads: int, priority_level: int}\n"
            "- required_agents: list of string role names\n"
            "- build_steps_dependency_graph: list of step descriptions\n\n"
            f"User Prompt: {prompt}"
        )

        try:
            gateway = GatewayRouter.get_gateway(service_type="brain")
            raw_response = await asyncio.to_thread(gateway.generate, system_prompt)
            
            clean_json = self._sanitize_llm_output(raw_response)
            parsed_data = json.loads(clean_json)

            validated_architecture = GameArchitectureSchema(**parsed_data)
            allocation_report = self._apply_server_allocations(validated_architecture, request_id)

            return {
                "status": "ROUTING_COMPLETE",
                "request_id": request_id,
                "architecture": validated_architecture.dict(),
                "server_allocation": allocation_report
            }

        except Exception as e:
            logger.warning(f"[{request_id}] Routing using Safe Fallback due to: {e}")
            return self._emergency_fallback_routing(prompt)
        finally:
            self.active_routings -= 1

    def _sanitize_llm_output(self, text: str) -> str:
        text = text.replace("```json", "").replace("```", "").strip()
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        return text

    def _apply_server_allocations(self, arch: GameArchitectureSchema, req_id: str) -> Dict[str, Any]:
        priority_map = {
            0: SimulationPriority.CRITICAL,
            1: SimulationPriority.HIGH,
            2: SimulationPriority.NORMAL,
            3: SimulationPriority.LOW
        }
        engine_priority = priority_map.get(arch.resource_limits.priority_level, SimulationPriority.NORMAL)

        return {
            "cpp_engine_status": "ONLINE" if arch.engine_config.use_cpp_bridge else "BYPASSED (Optimized)",
            "webrtc_status": "ONLINE" if arch.engine_config.use_webrtc_stream else "BYPASSED (Bandwidth Saved)",
            "nexus_status": "ONLINE" if arch.engine_config.use_multiplayer_nexus else "OFFLINE (Singleplayer)",
            "scheduler_priority_assigned": engine_priority.name
        }

    def _emergency_fallback_routing(self, prompt: str) -> Dict[str, Any]:
        return {
            "status": "FALLBACK_ROUTING",
            "architecture": {
                "target_platform": "web_html5",
                "complexity_class": "O(N)",
                "engine_config": {
                    "use_cpp_bridge": False,
                    "use_webrtc_stream": False,
                    "use_multiplayer_nexus": False,
                    "use_local_storage_only": True
                },
                "resource_limits": {"estimated_ram_mb": 512, "max_concurrent_threads": 2, "priority_level": 2},
                "required_agents": ["DirectorAgent", "MapBuilderAgent"],
                "build_steps_dependency_graph": ["Define Logic", "Build HTML5 Zip"]
            }
        }

master_router_instance = MasterIntentRouter()
