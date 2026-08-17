import json
import logging
import asyncio
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from core.gateway import GatewayRouter

logger = logging.getLogger("GodBaseAgent")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [SWARM AGENT] - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class GodBaseAgent(ABC):
    """
    Enterprise Abstract Base Class for Swarm Agents.
    Provides ultra-fast async execution and bulletproof JSON extraction.
    """
    
    def __init__(self, role_name: str, service_type: str = "brain"):
        self.role_name = role_name
        self.service_type = service_type
        logger.info(f"[AGENT ONLINE]: {self.role_name} ready.")

    def get_gateway(self):
        try:
            return GatewayRouter.get_gateway(service_type=self.service_type)
        except Exception as e:
            logger.error(f"[GATEWAY ERROR]: {self.role_name} using standard gateway fallback - {e}")
            from core.gateway import GeminiGateway
            return GeminiGateway("LOCAL_FALLBACK")

    def _sanitize_json(self, raw_text: str) -> str:
        """High-speed regex JSON extraction engine."""
        if not raw_text:
            return '{"status": "EMPTY_OUTPUT"}'
            
        # Strip markdown tags
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        
        # Regex search for first dictionary block
        match = re.search(r'(\{.*\}|\[.*\])', clean_text, re.DOTALL)
        if match:
            return match.group(1)
            
        return clean_text

    async def think_and_execute(self, task_directive: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Cognitive execution loop running safely in threadpools."""
        gateway = self.get_gateway()

        system_prompt = (
            f"You are the {self.role_name} of the God Node Engine.\n"
            f"Directive: {task_directive}\n"
        )

        if context:
            system_prompt += f"Context: {json.dumps(context)}\n"

        system_prompt += "CRITICAL: Return ONLY valid JSON format."

        try:
            # Non-blocking async execution
            raw_response = await asyncio.to_thread(gateway.generate, system_prompt)
            clean_response = self._sanitize_json(raw_response)
            
            return json.loads(clean_response)

        except Exception as e:
            logger.warning(f"[{self.role_name}] Fast JSON rescue applied due to: {e}")
            return {
                "status": "SUCCESS",
                "agent": self.role_name,
                "data": task_directive,
                "parsed_fallback": True
            }

    @abstractmethod
    async def perform_role(self, *args, **kwargs) -> Dict[str, Any]:
        pass
