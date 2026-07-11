from god_brain.agents.base_agent import GodBaseAgent

class QATesterAgent(GodBaseAgent):
    def __init__(self):
        super().__init__(role_name="QA Tester & Auto-Healer", service_type="brain")

    def perform_role(self, generated_code: str, error_logs: str = None) -> dict:
        """बने हुए कोड में बग्स ढूँढना या क्रैश होने पर उसे रिपेयर करना"""
        directive = (
            f"Review the provided game source code for logic bugs, memory leaks, and syntax errors. "
            f"If 'error_logs' are present, you MUST fix the code and return the repaired full code. "
            f"If no errors are found, optimize the rendering logic."
        )
        context = {
            "source_code": generated_code,
            "runtime_error_logs": error_logs if error_logs else "None. Perform static analysis."
        }
        return self.think_and_execute(task_directive=directive, context=context)
      
