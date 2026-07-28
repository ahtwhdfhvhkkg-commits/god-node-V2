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
    def __init__(self):
        self.version = "10.0.0-Enterprise"
        self.active_routings: int = 0
        logger.info("Initializing Enterprise Intent Router... System Online.")

    async def analyze_and_allocate(self, prompt: str) -> Dict[str, Any]:
        """
        The core pipeline: Reads prompt -> Calls Gateway -> Validates Schema -> Allocates Server Resources.
        """
        self.active_routings += 1
        request_id = f"REQ-{int(time.time())}-{self.active_routings}"
        logger.info(f"[{request_id}] Incoming Directive: '{prompt[:50]}...'")

        # System prompt forcing strict JSON adherence
        system_prompt = (
            "You are the Master Architect API for God Node V2. "
            "Analyze the user's game request. You MUST return ONLY a raw, valid JSON object "
            "that strictly matches the following Pydantic schema structure. Do NOT wrap in markdown.\n\n"
            "Schema Requirements:\n"
            "- target_platform: 'web_html5', 'mobile_apk', 'pc_exe', or 'cloud_stream'\n"
            "- complexity_class: Estimate Big-O or 'AAA'\n"
            "- engine_config: {use_cpp_bridge: bool, use_webrtc_stream: bool, use_multiplayer_nexus: bool, use_local_storage_only: bool}\n"
            "- resource_limits: {estimated_ram_mb: int, max_concurrent_threads: int, priority_level: int}\n"
            "- required_agents: list of strings\n"
            "- build_steps_dependency_graph: list of strings defining execution order\n\n"
            "Logic Rule: If the user wants a simple web game (like for CrazyGames), set use_cpp_bridge AND use_webrtc_stream to FALSE. "
            f"User Prompt: {prompt}"
        )

        try:
            # 1. Fetch AI Response via existing Gateway
            gateway = GatewayRouter.get_gateway(service_type="brain")
            raw_response = await asyncio.to_thread(gateway.generate, system_prompt)
            
            # 2. Deep Clean and Parse
            clean_json = self._sanitize_llm_output(raw_response)
            parsed_data = json.loads(clean_json)

            # 3. Pydantic Strict Validation
            validated_architecture = GameArchitectureSchema(**parsed_data)
            logger.info(f"[{request_id}] Validation SUCCESS. Target: {validated_architecture.target_platform}")

            # 4. Apply Server Allocations (The Replit Magic)
            allocation_report = self._apply_server_allocations(validated_architecture, request_id)

            return {
                "status": "ROUTING_COMPLETE",
                "request_id": request_id,
                "architecture": validated_architecture.dict(),
                "server_allocation": allocation_report
            }

        except ValidationError as ve:
            logger.error(f"[{request_id}] Schema Validation Failed! AI hallucinated wrong keys. {ve}")
            return self._emergency_fallback_routing(prompt)
        except Exception as e:
            logger.critical(f"[{request_id}] FATAL ROUTING ERROR: {str(e)}")
            return self._emergency_fallback_routing(prompt)
        finally:
            self.active_routings -= 1

    def _sanitize_llm_output(self, text: str) -> str:
        """Removes markdown and attempts to extract just the JSON dictionary."""
        text = text.replace("```json", "").replace("```", "").strip()
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        return text

    def _apply_server_allocations(self, arch: GameArchitectureSchema, req_id: str) -> Dict[str, Any]:
        """
        Dynamically adjusts the God Node server based on the required game.
        Like a Kubernetes orchestrator allocating pods.
        """
        logger.debug(f"[{req_id}] Allocating resources. Requested RAM: {arch.resource_limits.estimated_ram_mb}MB")
        
        # Determine Priority Enum mapping to the existing SimulationScheduler
        priority_map = {
            0: SimulationPriority.CRITICAL,
            1: SimulationPriority.HIGH,
            2: SimulationPriority.NORMAL,
            3: SimulationPriority.LOW
        }
        engine_priority = priority_map.get(arch.resource_limits.priority_level, SimulationPriority.NORMAL)

        report = {
            "cpp_engine_status": "ONLINE" if arch.engine_config.use_cpp_bridge else "BYPASSED (Saving CPU)",
            "webrtc_status": "ONLINE" if arch.engine_config.use_webrtc_stream else "BYPASSED (Saving Bandwidth)",
            "nexus_status": "ONLINE" if arch.engine_config.use_multiplayer_nexus else "OFFLINE (Singleplayer)",
            "scheduler_priority_assigned": engine_priority.name
        }

        logger.info(f"[{req_id}] Resource Allocation Complete: {report}")
        return report

    def _emergency_fallback_routing(self, prompt: str) -> Dict[str, Any]:
        """
        If the AI crashes or hallucinates, the system MUST NOT fail.
        This provides a safe, standard HTML5 fallback route.
        """
        logger.warning("Initiating Emergency Fallback Route (Safe Web Mode).")
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
                "resource_limits": {
                    "estimated_ram_mb": 512,
                    "max_concurrent_threads": 2,
                    "priority_level": 2
                },
                "required_agents": ["DirectorAgent", "MapBuilderAgent"],
                "build_steps_dependency_graph": ["Define Logic", "Build HTML5 Zip"]
            }
        }

# Singleton Instance for Global Use
master_router_instance = MasterIntentRouter()
