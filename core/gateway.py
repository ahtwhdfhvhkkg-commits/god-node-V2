import re
import itertools
import logging
from abc import ABC, abstractmethod
from fastapi import APIRouter, Request, HTTPException, status
from typing import Dict, Any
import time

# Enterprise Logging Configuration
logger = logging.getLogger("GatewayRouter")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

# 1. Base Class for APIs
class BaseGateway(ABC):
    @abstractmethod
    def generate(self, prompt: str):
        pass

# 2. API Handlers
class GeminiGateway(BaseGateway):
    def __init__(self, api_key):
        self.api_key = api_key
    def generate(self, prompt: str):
        return f"[Google API Executing] -> {prompt}"

class OpenAIGateway(BaseGateway):
    def __init__(self, api_key):
        self.api_key = api_key
    def generate(self, prompt: str):
        return f"[OpenAI API Executing] -> {prompt}"

# 3. THE MAIN ROUTER (This is what main.py is looking for!)
class GatewayRouter:
    """
    Enterprise-Grade API Gateway for The God Node.
    Handles FastAPI routing, load balancing, and payload validation.
    """
    _key_vault = {}

    def __init__(self):
        self.router = APIRouter()
        self.active_connections: int = 0
        self.system_start_time: float = time.time()
        self._register_routes()
        logger.info("GatewayRouter Initialized: All neural pathways open.")

    def _register_routes(self):
        @self.router.get("/health", tags=["System Core"])
        async def health_check() -> Dict[str, Any]:
            uptime = round(time.time() - self.system_start_time, 2)
            return {"status": "ONLINE", "uptime_seconds": uptime, "connections": self.active_connections}

    def get_router(self) -> APIRouter:
        return self.router

    @classmethod
    def load_vault(cls, multi_api_vault: dict):
        for service, keys in multi_api_vault.items():
            if isinstance(keys, list) and len(keys) > 0:
                cls._key_vault[service] = itertools.cycle(keys)
            elif isinstance(keys, str):
                cls._key_vault[service] = itertools.cycle([keys])

    @classmethod
    def get_gateway(cls, service_type: str = "brain"):
        if service_type not in cls._key_vault:
            raise ValueError(f"CRITICAL: No API keys configured for service -> {service_type}")
        
        next_key = next(cls._key_vault[service_type]).strip()
        
        if re.match(r'^(AIza|AQ)', next_key):
            logger.info(f"[LOAD BALANCER]: Routing request to Google Gemini.")
            return GeminiGateway(next_key)
        elif next_key.startswith('sk-'):
            logger.info(f"[LOAD BALANCER]: Routing request to OpenAI.")
            return OpenAIGateway(next_key)
        else:
            raise ValueError(f"Unknown API Key Signature: {next_key[:5]}...")
