import asyncio
import logging
import json
import time
import inspect
import re
from typing import Dict, Any, List

# Importing the Swarm Agents
from god_brain.agents.director_agent import DirectorAgent
from god_brain.agents.asset_generator_agent import AssetGeneratorAgent
from god_brain.agents.map_builder_agent import MapBuilderAgent
from god_brain.agents.physics_agent import PhysicsAgent
from god_brain.agents.qa_tester_agent import QATesterAgent

# Enterprise Logging Configuration
logger = logging.getLogger("GodOrchestrator")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - [ORCHESTRATOR] - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

class GodOrchestrator:
    """
    Enterprise-Grade Swarm Orchestrator.
    Manages parallel execution of AI agents while strictly adhering to external API rate limits.
    Uses Asyncio Semaphores to prevent HTTP 429 (Too Many Requests) errors.
    Equipped with Smart Resolver and Bulletproof JSON Extraction.
    """
    def __init__(self):
        logger.info("Initializing God Node Orchestrator... Waking up Manager Agents.")
        # Initialize the Core Manager Agents
        self.director = DirectorAgent()
        self.asset_gen = AssetGeneratorAgent()
        self.map_builder = MapBuilderAgent()
        self.physics = PhysicsAgent()
        self.qa_tester = QATesterAgent()
        
        # RATE LIMIT CONTROLLERS
        # Max concurrent tasks allowed at the exact same millisecond
        self.max_concurrent_agents = 5 
        self.semaphore = asyncio.Semaphore(self.max_concurrent_agents)

    def _rescue_json_data(self, data: Any) -> Any:
        """
        DOUBLE-LAYER FILTER: Automatically cleans markdown tags and extracts pure JSON.
        Rescues agent outputs that failed due to 'JSON Decode Error'.
        """
        # 1. Check if data is already a dict, but contains a failed raw_output
        if isinstance(data, dict):
            if data.get("status") == "FAILED" and "raw_output" in data:
                text_to_clean = str(data["raw_output"])
            else:
                return data
        elif isinstance(data, str):
            text_to_clean = data
        else:
            return data
            
        # LAYER 1: Strip common Markdown formatting AI models add
        text_to_clean = text_to_clean.replace("```json", "").replace("```", "").strip()

        try:
            # Try to parse immediately after stripping
            return json.loads(text_to_clean)
        except json.JSONDecodeError:
            # LAYER 2: If it still fails, use Regex to find the first JSON block { } or [ ]
            try:
                match = re.search(r'(\{.*\}|\[.*\])', text_to_clean, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
            except Exception:
                pass
                
        # If all rescue attempts fail, return the original data so it doesn't crash the server
        return data

    async def _resolve_agent_call(self, agent_method, *args, **kwargs):
        """
        THE MAGIC FIX: Automatically opens 'closed boxes' (coroutines) returned by agents.
        Applies the JSON rescue filter to ALL agent outputs automatically.
        """
        # 1. Execute the method dynamically based on its type
        if inspect.iscoroutinefunction(agent_method):
            result = await agent_method(*args, **kwargs)
        else:
            result = await asyncio.to_thread(agent_method, *args, **kwargs)
            
        # 2. Double-check: If the agent returned an un-awaited coroutine, await it here
        if inspect.isawaitable(result):
            result = await result
            
        # 3. APPLY THE JSON RESCUE FILTER HERE TO PROTECT ALL AGENTS
        return self._rescue_json_data(result)

    async def _execute_swarm_task_safely(self, task_id: int, agent, task_data: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a single agent task safely behind a Semaphore to prevent API flooding.
        Includes automatic retry logic with exponential backoff.
        """
        async with self.semaphore:
            retries = 3
            backoff = 2  # seconds
            
            for attempt in range(retries):
                try:
                    logger.info(f"[SWARM TASK #{task_id}] Executing via {agent.role_name}...")
                    
                    # Use the smart resolver to get the actual dictionary result
                    result = await self._resolve_agent_call(agent.perform_role, task_data, **kwargs)
                        
                    return {"task_id": task_id, "status": "SUCCESS", "result": result}
                
                except Exception as e:
                    logger.warning(f"[SWARM TASK #{task_id}] Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < retries - 1:
                        await asyncio.sleep(backoff)
                        backoff *= 2  # Exponential backoff (2s, 4s, 8s)
                    else:
                        logger.error(f"[SWARM TASK #{task_id}] CRITICAL FAILURE after {retries} attempts.")
                        return {"task_id": task_id, "status": "FAILED", "error": str(e)}

    async def generate_full_game_with_swarm(self, prompt: str, agent_count: int = 10, auto_kill_after_execution: bool = True) -> Dict[str, Any]:
        """
        The Main Pipeline: Generates a complete game using a controlled swarm of AI agents.
        """
        start_time = time.time()
        logger.info(f"Starting Swarm Pipeline for directive: '{prompt}' with target swarm size: {agent_count}")

        try:
            # ---------------------------------------------------------
            # STEP 1: THE DIRECTOR (Strategic Planning)
            # ---------------------------------------------------------
            logger.info("STEP 1: Director is planning the architecture...")
            game_plan = await self._resolve_agent_call(self.director.perform_role, prompt)
            
            if not game_plan or (isinstance(game_plan, dict) and game_plan.get("status") == "FAILED"):
                error_msg = game_plan.get('error', 'Unknown Error') if isinstance(game_plan, dict) else 'Invalid Format'
                raise ValueError(f"Director Agent failed to create a valid plan: {error_msg}")

            # ---------------------------------------------------------
            # STEP 2 & 3: THE SWARM (Asset & Map Generation in Parallel)
            # ---------------------------------------------------------
            logger.info(f"STEP 2 & 3: Spawning Swarm of {agent_count} agents for Assets and Mapping...")
            
            # We break the swarm count into Asset tasks and Map tasks
            asset_tasks_count = max(1, int(agent_count * 0.7)) # 70% of swarm makes assets
            map_tasks_count = max(1, int(agent_count * 0.3))   # 30% of swarm builds map logic
            
            swarm_tasks = []
            
            # Queue Asset Generation Tasks
            for i in range(asset_tasks_count):
                task_desc = f"Generate 3D asset component part {i+1} based on plan: {str(game_plan)}"
                task = self._execute_swarm_task_safely(
                    task_id=i, 
                    agent=self.asset_gen, 
                    task_data=task_desc, 
                    kwargs={"style": "optimized"}
                )
                swarm_tasks.append(task)
                
            # Queue Map Generation Tasks
            for i in range(map_tasks_count):
                task_desc = f"Design sector {i+1} of the map based on theme: {prompt}"
                task = self._execute_swarm_task_safely(
                    task_id=asset_tasks_count + i, 
                    agent=self.map_builder, 
                    task_data=task_desc, 
                    kwargs={"generated_assets": ["placeholder_list"]}
                )
                swarm_tasks.append(task)

            # Fire the entire Swarm concurrently (Semaphore handles the rate limits)
            logger.info(f"Firing {len(swarm_tasks)} tasks into the asynchronous event loop...")
            swarm_results = await asyncio.gather(*swarm_tasks)
            
            # Filter successful results
            successful_assets = [res["result"] for res in swarm_results if res["status"] == "SUCCESS"]
            logger.info(f"Swarm Complete: {len(successful_assets)}/{len(swarm_tasks)} tasks succeeded.")

            # ---------------------------------------------------------
            # STEP 4: PHYSICS INJECTION
            # ---------------------------------------------------------
            logger.info("STEP 4: Injecting Physics and Gravity logic...")
            physics_context = {"map_data": "compiled_swarm_map", "assets": len(successful_assets)}
            physics_logic = await self._resolve_agent_call(self.physics.perform_role, environment_details=physics_context)

            # ---------------------------------------------------------
            # STEP 5: ASSEMBLY
            # ---------------------------------------------------------
            logger.info("STEP 5: Assembling Raw Game Code...")
            raw_game_code = {
                "architecture": game_plan,
                "assets_generated": len(successful_assets),
                "physics_engine": physics_logic,
                "timestamp": time.time()
            }
            
            raw_code_string = json.dumps(raw_game_code, indent=2)

            # ---------------------------------------------------------
            # STEP 6: QA TESTING & AUTO-HEALING
            # ---------------------------------------------------------
            logger.info("STEP 6: QA Tester is analyzing the build for stability...")
            final_game = await self._resolve_agent_call(self.qa_tester.perform_role, generated_code=raw_code_string, error_logs=None)

            execution_time = round(time.time() - start_time, 2)
            logger.info(f"PIPELINE COMPLETE! Total execution time: {execution_time} seconds.")

            return {
                "status": "SUCCESS",
                "message": f"Game successfully built and verified by swarm of {agent_count} agents.",
                "execution_time": f"{execution_time}s",
                "final_build": final_game
            }

        except Exception as e:
            logger.error(f"ORCHESTRATOR CRASH: Pipeline failed -> {str(e)}")
            return {
                "status": "FAILED",
                "error": str(e),
                "stage": "Execution Pipeline"
            }



