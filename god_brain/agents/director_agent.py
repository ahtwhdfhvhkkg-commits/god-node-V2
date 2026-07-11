from god_brain.agents.base_agent import GodBaseAgent

class DirectorAgent(GodBaseAgent):
    def __init__(self):
        super().__init__(role_name="Game Director", service_type="brain")

    def perform_role(self, game_idea: str) -> dict:
        """खिलाड़ी (या तुम्हारे) प्रॉम्प्ट से गेम के रूल्स और आर्किटेक्चर बनाना"""
        directive = (
            f"Analyze the following game concept: '{game_idea}'. "
            f"Generate a strict technical architecture including: "
            f"1. Core Gameplay Loop, 2. Win/Loss Conditions, 3. Required 3D Assets, 4. Physics Requirements. "
            f"Output must be actionable steps for other AI agents."
        )
        return self.think_and_execute(task_directive=directive)
      
