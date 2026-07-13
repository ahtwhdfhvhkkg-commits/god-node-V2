import asyncio
import logging
import time
import json
import re
from typing import Dict, List, Any, Optional

# ---------------------------------------------------------
# ENTERPRISE LOGGING CONFIGURATION
# ---------------------------------------------------------
logger = logging.getLogger("UniversalApiNexus")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - [NEXUS CORE] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

# ---------------------------------------------------------
# UNIVERSAL API NEXUS (MULTI-BRAIN ROUTER)
# ---------------------------------------------------------
class MultiBrainRouter:
    """
    Enterprise-Grade Universal Mixture of Experts (MoE) Router.
    Automatically detects, configures, and routes tasks to ANY AI API provided.
    Implements dynamic free-tier rate limiting, auto-fallback, and agnostic routing.
    """
    
    # Pre-mapped Free Tier Limits (RPM = Requests Per Minute, CONCURRENT = Max parallel)
    # If an unknown API is detected, it falls back to the SAFE_DEFAULT.
    KNOWN_LIMITS = {
        "gemini": {"rpm": 15, "concurrent": 5},
        "openai": {"rpm": 3, "concurrent": 1},
        "openrouter": {"rpm": 20, "concurrent": 10},
        "claude": {"rpm": 5, "concurrent": 1},
        "groq": {"rpm": 30, "concurrent": 10},
        "elevenlabs": {"rpm": 30, "concurrent": 5},
        "huggingface": {"rpm": 10, "concurrent": 2},
        "runway": {"rpm": 5, "concurrent": 1},
        "safe_default": {"rpm": 5, "concurrent": 1} # For ANY unknown API
    }

    def __init__(self, api_vault: Dict[str, List[str]]):
        """
        Dynamically initializes the Nexus based on whatever keys exist in the vault.
        """
        self.raw_vault = api_vault
        self.active_providers = {}
        self.rate_trackers = {}
        self.semaphores = {}
        
        self.metrics = {
            "total_requests": 0,
            "successful_routes": 0,
            "fallbacks_triggered": 0,
            "rate_limit_pauses": 0
        }

        self._initialize_universal_registry()
        logger.info(f"Universal Nexus Initialized. Active AI Brains: {list(self.active_providers.keys())}")

    def _initialize_universal_registry(self):
        """Scans the provided vault and automatically registers any API found."""
        for provider_name, keys in self.raw_vault.items():
            if keys and isinstance(keys, list) and len(keys) > 0 and keys[0]:
                clean_name = provider_name.lower().strip()
                self.active_providers[clean_name] = keys
                
                # Fetch known limits or apply Safe Default for unknown APIs
                limits = self.KNOWN_LIMITS.get(clean_name, self.KNOWN_LIMITS["safe_default"])
                
                self.rate_trackers[clean_name] = {
                    "rpm_limit": limits["rpm"],
                    "current_minute_calls": 0,
                    "minute_start": time.time()
                }
                
                # Create a strict concurrency lock for this specific provider
                self.semaphores[clean_name] = asyncio.Semaphore(limits["concurrent"])

    async def _throttle_and_lock(self, provider: str):
        """
        Universal Traffic Controller: Prevents 429 Errors for ANY API.
        Tracks time and pauses execution only if the specific provider is maxed out.
        """
        tracker = self.rate_trackers.get(provider)
        if not tracker:
            return

        current_time = time.time()
        
        # Reset counter if a minute has passed
        if current_time - tracker["minute_start"] >= 60:
            tracker["current_minute_calls"] = 0
            tracker["minute_start"] = current_time

        # If limit reached, calculate wait time and sleep
        if tracker["current_minute_calls"] >= tracker["rpm_limit"]:
            wait_time = 60.5 - (current_time - tracker["minute_start"])
            if wait_time > 0:
                logger.warning(f"[RATE LIMIT] {provider.upper()} RPM ({tracker['rpm_limit']}) hit. Sleeping {wait_time:.1f}s to protect Free Tier...")
                self.metrics["rate_limit_pauses"] += 1
                await asyncio.sleep(wait_time)
                # Reset after waking up
                tracker["current_minute_calls"] = 0
                tracker["minute_start"] = time.time()
                
        tracker["current_minute_calls"] += 1

    def _determine_best_provider(self, directive: str) -> List[str]:
        """
        Analyzes the prompt to build a Fallback Chain (Plan A, Plan B, Plan C).
        Does not rely on hardcoded 'if openai'. Dynamically checks active providers.
        """
        directive_lower = directive.lower()
        available = list(self.active_providers.keys())
        
        if not available:
            raise RuntimeError("CRITICAL: Vault is completely empty. No AI APIs available.")

        fallback_chain = []

        # CATEGORY: Heavy Code / Logic / Architecture
        if any(kw in directive_lower for kw in ["code", "script", "class", "function", "debug", "architecture"]):
            preferred = ["openai", "claude", "openrouter", "groq", "gemini"]
            fallback_chain = [p for p in preferred if p in available]
            
        # CATEGORY: 3D Assets / Visuals
        elif any(kw in directive_lower for kw in ["3d", "texture", "model", "visual", "render"]):
            preferred = ["runway", "openrouter", "gemini", "openai"]
            fallback_chain = [p for p in preferred if p in available]
            
        # CATEGORY: Audio / SFX
        elif any(kw in directive_lower for kw in ["audio", "sound", "sfx", "voice"]):
            preferred = ["elevenlabs", "openai", "gemini"]
            fallback_chain = [p for p in preferred if p in available]
            
        # CATEGORY: Fast Logic / Map Generation (Cost effective)
        else:
            preferred = ["gemini", "groq", "openrouter", "claude", "openai"]
            fallback_chain = [p for p in preferred if p in available]

        # If none of our preferred matched the vault, just use whatever is available
        if not fallback_chain:
            fallback_chain = available

        return fallback_chain

    async def analyze_and_route_task(self, directive: str, system_context: str = "") -> Dict[str, Any]:
        """
        The Master Routing Function. Tries the best provider, and if it fails or is busy, 
        seamlessly falls back to the next available API in the chain.
        """
        self.metrics["total_requests"] += 1
        provider_chain = self._determine_best_provider(directive)
        
        last_error = ""

        for provider in provider_chain:
            try:
                # 1. Acquire concurrency lock for this specific API
                async with self.semaphores[provider]:
                    # 2. Check and apply RPM throttling
                    await self._throttle_and_lock(provider)
                    
                    # 3. Execute Task
                    result = await self._execute_universal_task(provider, directive, system_context)
                    
                    self.metrics["successful_routes"] += 1
                    return result

            except Exception as e:
                logger.warning(f"[FALLBACK TRIGGERED] Provider '{provider}' failed: {str(e)}. Trying next in chain...")
                self.metrics["fallbacks_triggered"] += 1
                last_error = str(e)
                continue # Try the next provider in the fallback chain

        # If all providers in the chain fail
        logger.error(f"[NEXUS CRITICAL] All available AI Brains failed. Last Error: {last_error}")
        return {
            "status": "FAILED",
            "msg": "Complete Swarm Failure. All APIs exhausted.",
            "error": last_error
        }

    async def _execute_universal_task(self, provider: str, prompt: str, context: str) -> Dict[str, Any]:
        """
        Generic execution engine. In production, this uses aiohttp to hit the specific 
        REST endpoints based on the provider name.
        """
        api_keys = self.active_providers[provider]
        current_key = api_keys[0] # In future, implement round-robin key rotation here
        
        logger.info(f"[EXECUTION] Firing API Request to -> {provider.upper()} Engine...")
        
        # ------------------------------------------------------------------
        # ENTERPRISE PLACEHOLDER: HTTP CLIENT INJECTION POINT
        # Here you will use aiohttp.ClientSession() to make the actual POST 
        # request based on the provider's URL structure.
        # ------------------------------------------------------------------
        
        # Simulating network latency based on provider weight
        simulated_delay = 1.0 if provider in ["gemini", "groq"] else 2.5
        await asyncio.sleep(simulated_delay) 
        
        return {
            "status": "SUCCESS",
            "brain_used": provider.upper(),
            "response": f"[{provider.upper()} API] Task processed successfully. Raw logic generated.",
            "execution_time_ms": int(simulated_delay * 1000)
        }

    def get_system_metrics(self) -> Dict[str, Any]:
        return self.metrics
  
