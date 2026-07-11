import json
from abc import ABC, abstractmethod

# पिछले मल्टी-एपीआई राउटर के साथ 100% सिंक
try:
    from core.gateway import GatewayResolver
except ImportError:
    raise RuntimeError("CRITICAL: GatewayResolver not found. Base Agent cannot start.")

class GodBaseAgent(ABC):
    def __init__(self, role_name: str, service_type: str = "brain"):
        self.role_name = role_name
        self.service_type = service_type

    def get_ai_gateway(self):
        """लोड बैलेंसर से इस एजेंट के लिए सबसे फ्री API Key (चाबी) निकालना"""
        return GatewayResolver.get_gateway(service_type=self.service_type)

    def think_and_execute(self, task_directive: str, context: dict = None) -> dict:
        """
        यह मेन फंक्शन है जिससे सारे एजेंट्स सोचेंगे। 
        हम AI को सख्त निर्देश देंगे कि वह सिर्फ JSON फॉर्मेट में जवाब दे, 
        ताकि हमारे कोड में एरर न आए।
        """
        gateway = self.get_ai_gateway()
        
        system_prompt = (
            f"You are the {self.role_name} of the God Node Engine. "
            f"Your task: {task_directive}. "
        )
        
        if context:
            system_prompt += f"\nContext/Previous Data: {json.dumps(context)} "
            
        system_prompt += (
            "\nCRITICAL INSTRUCTION: You must ONLY reply in raw, valid JSON format. "
            "Do not include markdown tags like ```json or any conversational text. "
            "Example format: {'status': 'success', 'data': 'your actual code or logic'}"
        )

        print(f"[AGENT ACTIVATED]: {self.role_name} is processing task...")
        
        raw_response = gateway.generate(system_prompt)
        
        # आउटपुट को क्लीन करना (अगर AI ने गलती से कचरा दे दिया हो)
        clean_response = raw_response.replace("```json\n", "").replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(clean_response)
        except json.JSONDecodeError as e:
            print(f"[AGENT ERROR]: {self.role_name} failed to return valid JSON. Auto-fixing...")
            return {
                "status": "failed",
                "error": "JSON Decode Error",
                "raw_output": clean_response
            }

    @abstractmethod
    def perform_role(self, *args, **kwargs):
        """हर एजेंट अपना काम अलग तरीके से करेगा (इसे अगली फाइलों में डिफाइन करेंगे)"""
        pass
  
