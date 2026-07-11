from god_brain.agents.base_agent import GodBaseAgent

class AssetGeneratorAgent(GodBaseAgent):
    def __init__(self):
        super().__init__(role_name="3D Asset Generator", service_type="brain")

    def perform_role(self, asset_description: str, style: str = "realistic") -> dict:
        """कमांड को पढ़कर 3D मॉडल (Vertices, Faces, Materials) का डेटा जनरेट करना"""
        directive = (
            f"Generate a detailed 3D model architecture for: '{asset_description}'. "
            f"Visual Style: {style}. "
            f"Provide the exact geometric parameters (vertices, textures, materials) "
            f"compatible with Three.js or Unreal Engine object structures. "
            f"Ensure the polygon count is optimized for cloud streaming."
        )
        return self.think_and_execute(task_directive=directive)
      
