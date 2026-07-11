import re
import itertools
from abc import ABC, abstractmethod

# 1. Base Class
class BaseGateway(ABC):
    @abstractmethod
    def generate(self, prompt: str):
        pass

# 2. Google Gemini Handler
class GeminiGateway(BaseGateway):
    def __init__(self, api_key):
        self.api_key = api_key
    def generate(self, prompt: str):
        # असली सर्वर में यहाँ Google Generative AI का SDK कॉल होगा
        return f"[Google API Executing] -> {prompt}"

# 3. OpenAI / OpenRouter Handler
class OpenAIGateway(BaseGateway):
    def __init__(self, api_key):
        self.api_key = api_key
    def generate(self, prompt: str):
        # असली सर्वर में यहाँ OpenRouter का API कॉल होगा
        return f"[OpenRouter API Executing] -> {prompt}"

# 4. THE GOD LEVEL ROUTER (Load Balancer & Key Rotator)
class GatewayResolver:
    _key_vault = {}

    @classmethod
    def load_vault(cls, multi_api_vault: dict):
        """
        यहाँ तुम्हारी मल्टीपल चाबियाँ लोड होंगी।
        Format: {"brain": ["key1", "key2"], "audio": ["key3", "key4"]}
        """
        for service, keys in multi_api_vault.items():
            if isinstance(keys, list) and len(keys) > 0:
                cls._key_vault[service] = itertools.cycle(keys)
            elif isinstance(keys, str):
                cls._key_vault[service] = itertools.cycle([keys])

    @classmethod
    def get_gateway(cls, service_type: str = "brain"):
        """जिस सर्विस (Brain, Audio, Assets) के लिए गेटवे चाहिए, उसकी अगली चाबी निकालेगा"""
        if service_type not in cls._key_vault:
            raise ValueError(f"CRITICAL: No API keys configured for service -> '{service_type}'")
        
        # रोटेशन में से अगली चाबी (Next Key) उठाना
        next_key = next(cls._key_vault[service_type]).strip()
        
        # ऑटो-डिटेक्ट: चाबी Google की है या OpenRouter की
        if re.match(r'^(AIza|AQ)', next_key):
            print(f"[LOAD BALANCER]: Routing '{service_type}' request to Google Gemini.")
            return GeminiGateway(next_key)
        elif next_key.startswith('sk-'):
            print(f"[LOAD BALANCER]: Routing '{service_type}' request to OpenRouter.")
            return OpenAIGateway(next_key)
        else:
            raise ValueError(f"Unknown API Key Signature: {next_key[:5]}...")

