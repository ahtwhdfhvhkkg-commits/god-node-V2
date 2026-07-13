import json
import logging
import asyncio
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

# The critical fix: Importing GatewayRouter instead of GatewayResolver
from core.gateway import GatewayRouter

# Enterprise Logging Configuration
logger = logging.getLogger("GodBaseAgent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

class GodBaseAgent(ABC):
    """
    Enterprise-Grade Abstract Base Class for all Swarm Agents.
    Enforces strict JSON output, handles API gateway routing, and supports asynchronous swarm execution.
    """
    
    def __init__(self, role_name: str, service_type: str = "brain"):
        self.role_name = role_name
        self.service_type = service_type
        logger.info(f"[AGENT INIT]: {self.role_name} comes online. Awaiting directives.")

    def get_gateway(self):
        """Retrieves the optimal API Key/Gateway from the Load Balancer."""
        try:
            # Using the updated GatewayRouter class methods
            return GatewayRouter.get_gateway(service_type=self.service_type)
        except Exception as e:
            logger.error(f"CRITICAL: Gateway routing failed for {self.role_name} - {str(e)}")
            raise RuntimeError(f"GatewayRouter not found or unconfigured. {str(e)}")

    def _sanitize_json(self, raw_text: str) -> str:
        """Advanced regex-based JSON sanitizer to handle LLM formatting errors."""
        # Remove markdown code blocks if the LLM adds them
        clean_text = re.sub(r'^```json\s*', '', raw_text, flags=re.MULTILINE)
        clean_text = re.sub(r'^```\s*', '', clean_text, flags=re.MULTILINE)
        
        # Find the first '{' and the last '}' to extract only the JSON object
        start_idx = clean_text.find('{')
        end_idx = clean_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            return clean_text[start_idx:end_idx+1]
        return clean_text.strip()

    async def think_and_execute(self, task_directive: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        The core cognitive engine for the agent.
        Made ASYNCHRONOUS to allow the Orchestrator to spawn 200 agents concurrently.
        """
        gateway = self.get_gateway()

        system_prompt = (
            f"You are the {self.role_name} of the God Node Engine. "
            f"Your current directive: {task_directive}\n"
        )

        if context:
            system_prompt += f"\nContext/Previous Data: {json.dumps(context)}\n"

        system_prompt += (
            "\nCRITICAL INSTRUCTION: You must ONLY reply in raw, valid JSON format. "
            "Do not include markdown tags like ```json or any conversational text. "
            "Example format: {\"status\": \"success\", \"data\": \"your output here\"}"
        )

        logger.info(f"[AGENT ACTIVATED]: {self.role_name} is processing task asynchronously...")

        try:
            # Running the synchronous gateway.generate() in a thread pool 
            # to prevent blocking the FastAPI event loop during a 200-agent swarm.
            raw_response = await asyncio.to_thread(gateway.generate, system_prompt)
            
            clean_response = self._sanitize_json(raw_response)
            
            # Parse the JSON response
            parsed_json = json.loads(clean_response)
            return parsed_json

        except json.JSONDecodeError as e:
            logger.error(f"[AGENT ERROR]: {self.role_name} failed to return valid JSON. Attempting auto-fix...")
            logger.debug(f"Raw Output that failed: {raw_response}")
            return {
                "status": "FAILED",
                "error": "JSON Decode Error. LLM returned malformed syntax.",
                "raw_output": raw_response if 'raw_response' in locals() else "N/A"
            }
        except Exception as e:
            logger.error(f"[AGENT CRITICAL]: {self.role_name} encountered a fatal error: {str(e)}")
            return {
                "status": "FAILED",
                "error": str(e)
            }

    @abstractmethod
    async def perform_role(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Every specific agent (Director, Physics, etc.) MUST implement this method.
        It defines their unique role in the Swarm.
        """
        pass
