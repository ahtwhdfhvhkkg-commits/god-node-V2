from god_brain.agents.base_agent import GodBaseAgent

class MapBuilderAgent(GodBaseAgent):
    def __init__(self):
        super().__init__(role_name="Environment & Map Builder", service_type="brain")

    def perform_role(self, environment_theme: str, generated_assets: list) -> dict:
        """3D दुनिया बनाना और उसमें मर्सिडीज़ या बिल्डिंग्स को सही जगह (X, Y, Z) पर रखना"""
        directive = (
            f"Design a 3D environment based on the theme: '{environment_theme}'. "
            f"You have the following 3D assets ready to place: {generated_assets}. "
            f"Generate the exact X, Y, Z coordinates, rotation, lighting positions (Sun/Shadows), "
            f"and collision boundaries for this map."
        )
        return self.think_and_execute(task_directive=directive)
      
