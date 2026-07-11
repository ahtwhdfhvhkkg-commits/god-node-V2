# सारे एजेंट्स को इम्पोर्ट करना
from god_brain.agents.director_agent import DirectorAgent
from god_brain.agents.asset_generator_agent import AssetGeneratorAgent
from god_brain.agents.map_builder_agent import MapBuilderAgent
from god_brain.agents.physics_agent import PhysicsAgent
from god_brain.agents.qa_tester_agent import QATesterAgent

class GodOrchestrator:
    def __init__(self):
        # पूरी टीम को काम पर लगाना (Initialize)
        self.director = DirectorAgent()
        self.asset_gen = AssetGeneratorAgent()
        self.map_builder = MapBuilderAgent()
        self.physics = PhysicsAgent()
        self.qa_tester = QATesterAgent()

    def generate_full_game(self, user_prompt: str) -> dict:
        """यह मेन पाइपलाइन है जहाँ गेम 5 स्टेप्स में बनेगा"""
        print(f"\n[ORCHESTRATOR]: Starting God Node Pipeline for -> '{user_prompt}'")
        
        try:
            # स्टेप 1: डायरेक्टर गेम के रूल्स और आर्किटेक्चर तय करेगा
            print("[STEP 1]: Director is planning the game...")
            game_plan = self.director.perform_role(user_prompt)
            
            # स्टेप 2: एसेट जनरेटर 3D मॉडल (कार, पत्थर आदि) बनाएगा
            print("[STEP 2]: Forging 3D Assets...")
            # डायरेक्टर के प्लान से एसेट्स की लिस्ट निकालकर जनरेट करना
            assets_needed = game_plan.get("data", "basic environment elements")
            assets = self.asset_gen.perform_role(asset_description=str(assets_needed))
            
            # स्टेप 3: मैप बिल्डर 3D दुनिया बनाएगा और एसेट्स को वहां रखेगा
            print("[STEP 3]: Building the 3D Map...")
            map_data = self.map_builder.perform_role(environment_theme=user_prompt, generated_assets=[assets])
            
            # स्टेप 4: फिजिक्स एजेंट गेम में ग्रेविटी और टक्कर के नियम डालेगा
            print("[STEP 4]: Injecting Physics and Gravity...")
            physics_logic = self.physics.perform_role(environment_details=map_data)
            
            # स्टेप 5: इन सबको जोड़कर एक कच्चा कोड (Raw Code) बनाना
            raw_game_code = {
                "architecture": game_plan,
                "assets": assets,
                "world_map": map_data,
                "physics": physics_logic
            }
            
            # स्टेप 6: QA टेस्टर (ऑटो-हीलर) इस पूरे कोड को चेक करेगा और फिक्स करेगा
            print("[STEP 5]: QA Tester is scanning for bugs and finalizing...")
            final_game = self.qa_tester.perform_role(generated_code=str(raw_game_code))
            
            print("[ORCHESTRATOR]: GAME GENERATION COMPLETE! 🚀")
            return {
                "status": "SUCCESS",
                "message": "Game successfully built and verified by all agents.",
                "final_build": final_game
            }
            
        except Exception as e:
            print(f"[ORCHESTRATOR CRASH]: Pipeline failed -> {str(e)}")
            return {"status": "FAILED", "error": str(e)}

