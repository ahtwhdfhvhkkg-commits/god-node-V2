import time
import json
import asyncio
import aiohttp
import logging
import traceback
from typing import Dict, Any, Optional

# Enterprise Logging Setup
logger = logging.getLogger("MultiBrainRouter")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - [NEXUS] - %(message)s'))
    logger.addHandler(ch)

class MultiBrainRouter:
    """
    The Universal API Nexus (ENTERPRISE EDITION).
    Dynamically analyzes directives and routes them to the most capable AI Brain using LIVE API endpoints.
    Equipped with Auto-Retry, Fallback chains, and Advanced Error Handling.
    """
    def __init__(self, api_vault: Dict[str, list]):
        logger.info("Initializing Multi-Brain Router (100% LIVE MODE)...")
        self.api_vault = api_vault
        
        # Extracting Master Keys securely from the Vault
        self.keys = {
            "openai": self._get_key("openai"),
            "gemini": self._get_key("gemini"),
            "claude": self._get_key("claude"),
            "openrouter": self._get_key("openrouter"),
            "elevenlabs": self._get_key("elevenlabs")
        }
        
        # Load balancing / Rate limit settings
        self.max_retries = 3
        self.backoff_factor = 2

    def _get_key(self, provider: str) -> Optional[str]:
        """Safely retrieves the first available key for a provider."""
        keys = self.api_vault.get(provider, [])
        return keys[0] if keys else None

    # ---------------------------------------------------------
    # 1. THE SMART ROUTING ENGINE
    # ---------------------------------------------------------
    async def analyze_and_route_task(self, directive: str) -> Dict[str, Any]:
        """Analyzes the prompt and dynamically routes it to the correct AI Model."""
        start_time = time.time()
        directive_lower = directive.lower()
        
        response_text = None
        brain_used = "UNKNOWN"
        error_msg = None

        try:
            # PATH A: AUDIO / VOICE COMMANDS -> ElevenLabs
            if any(word in directive_lower for word in ["voice", "audio", "speak", "sound"]):
                brain_used = "ELEVENLABS"
                if self.keys["elevenlabs"]:
                    response_text = await self._call_elevenlabs(directive)
                else:
                    error_msg = "ElevenLabs key missing."

            # PATH B: HIGH-LEVEL LOGIC & CODING -> OpenAI (GPT-4o) or Claude
            elif any(word in directive_lower for word in ["code", "script", "python", "html", "logic", "system", "c++"]):
                if self.keys["openai"]:
                    brain_used = "OPENAI"
                    response_text = await self._call_openai(directive)
                elif self.keys["claude"]:
                    brain_used = "CLAUDE"
                    response_text = await self._call_claude(directive)
                else:
                    error_msg = "Both OpenAI and Claude keys are missing for coding task."

            # PATH C: CREATIVE, FAST & GENERAL -> Gemini or OpenRouter
            else:
                if self.keys["gemini"]:
                    brain_used = "GEMINI"
                    response_text = await self._call_gemini(directive)
                elif self.keys["openrouter"]:
                    brain_used = "OPENROUTER"
                    response_text = await self._call_openrouter(directive)
                else:
                    error_msg = "Gemini and OpenRouter keys are missing for general task."

            # PATH D: FALLBACK MECHANISM (If chosen brain failed or keys missing)
            if not response_text or error_msg:
                logger.warning(f"Primary routing failed ({error_msg}). Initiating Fallback Chain...")
                for fallback_brain in ["gemini", "openai", "openrouter", "claude"]:
                    if self.keys[fallback_brain]:
                        logger.info(f"Fallback to {fallback_brain.upper()}...")
                        brain_used = fallback_brain.upper()
                        if fallback_brain == "gemini": response_text = await self._call_gemini(directive)
                        elif fallback_brain == "openai": response_text = await self._call_openai(directive)
                        elif fallback_brain == "openrouter": response_text = await self._call_openrouter(directive)
                        elif fallback_brain == "claude": response_text = await self._call_claude(directive)
                        
                        if response_text and not response_text.startswith("[CRITICAL"): 
                            break # Fallback succeeded!

            # Final validation
            if not response_text:
                raise ValueError("All AI brains failed or no valid API keys were found in the Vault.")

        except Exception as e:
            logger.error(f"Nexus Crash: {str(e)}\n{traceback.format_exc()}")
            return {"status": "FAILED", "error": f"NEXUS HALT: {str(e)}"}

        execution_time = round((time.time() - start_time) * 1000)
        
        return {
            "status": "SUCCESS",
            "brain_used": brain_used,
            "response": response_text,
            "execution_time_ms": execution_time
        }

    # ---------------------------------------------------------
    # 2. ADVANCED API REQUEST HANDLER (WITH RETRIES)
    # ---------------------------------------------------------
    async def _safe_async_post(self, url: str, headers: dict, payload: dict, provider_name: str) -> str:
        """Centralized HTTP requester with auto-retry and exponential backoff."""
        async with aiohttp.ClientSession() as session:
            for attempt in range(self.max_retries):
                try:
                    async with session.post(url, headers=headers, json=payload, timeout=60) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429: # Rate Limit Hit
                            logger.warning(f"[{provider_name}] Rate Limit Hit. Retrying in {self.backoff_factor ** attempt}s...")
                            await asyncio.sleep(self.backoff_factor ** attempt)
                            continue
                        else:
                            error_text = await response.text()
                            logger.error(f"[{provider_name}] HTTP {response.status}: {error_text}")
                            return {"error": f"HTTP {response.status}: {error_text}"}
                except asyncio.TimeoutError:
                    logger.warning(f"[{provider_name}] Timeout on attempt {attempt + 1}")
                except Exception as e:
                    logger.error(f"[{provider_name}] Request crash: {str(e)}")
                
                # Wait before retry
                await asyncio.sleep(self.backoff_factor ** attempt)
                
        return {"error": f"Max retries ({self.max_retries}) exceeded for {provider_name}."}

    # ---------------------------------------------------------
    # 3. REAL API CONNECTIONS
    # ---------------------------------------------------------

    async def _call_openai(self, prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.keys['openai']}"}
        payload = {
            "model": "gpt-4o",
            "messages": [{"role": "system", "content": "You are the God Node AGI. Provide pure, accurate output."}, {"role": "user", "content": prompt}],
            "temperature": 0.5
        }
        res = await self._safe_async_post(url, headers, payload, "OPENAI")
        if "error" in res: return f"[CRITICAL ERROR] OpenAI: {res['error']}"
        return res["choices"][0]["message"]["content"]

    async def _call_gemini(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.keys['gemini']}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {"parts": [{"text": "You are the God Node AGI. Provide pure, accurate output."}]},
            "contents": [{"parts": [{"text": prompt}]}]
        }
        res = await self._safe_async_post(url, headers, payload, "GEMINI")
        if "error" in res: return f"[CRITICAL ERROR] Gemini: {res['error']}"
        return res["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_claude(self, prompt: str) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.keys['claude'],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 4000,
            "system": "You are the God Node AGI. Provide pure, accurate output.",
            "messages": [{"role": "user", "content": prompt}]
        }
        res = await self._safe_async_post(url, headers, payload, "CLAUDE")
        if "error" in res: return f"[CRITICAL ERROR] Claude: {res['error']}"
        return res["content"][0]["text"]

    async def _call_openrouter(self, prompt: str) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.keys['openrouter']}", "Content-Type": "application/json"}
        payload = {
            "model": "meta-llama/llama-3-70b-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }
        res = await self._safe_async_post(url, headers, payload, "OPENROUTER")
        if "error" in res: return f"[CRITICAL ERROR] OpenRouter: {res['error']}"
        return res["choices"][0]["message"]["content"]

    async def _call_elevenlabs(self, prompt: str) -> str:
        # For Audio, we just return a success string or base64 stream logic here
        # (Assuming the prompt is text to be converted to speech)
        voice_id = "21m00Tcm4TlvDq8ikWAM" # Rachel default
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": self.keys['elevenlabs'], "Content-Type": "application/json"}
        payload = {"text": prompt, "model_id": "eleven_monolingual_v1"}
        
        # Audio returns binary, not JSON. Handled separately to prevent crash.
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                    if response.status == 200:
                        return "[AUDIO GENERATED] Successfully streamed bytes from ElevenLabs."
                    else:
                        error_text = await response.text()
                        return f"[CRITICAL ERROR] ElevenLabs: HTTP {response.status}: {error_text}"
            except Exception as e:
                return f"[CRITICAL ERROR] ElevenLabs Crash: {str(e)}"
        
