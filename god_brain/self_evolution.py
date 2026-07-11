import os
import ast
import shutil
import datetime

class EvolutionEngine:
    def __init__(self, ai_gateway, base_dir="."):
        self.ai = ai_gateway
        self.base_dir = base_dir
        self.backup_dir = os.path.join(self.base_dir, "backups")
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def shadow_test_syntax(self, code_string: str) -> bool:
        try:
            ast.parse(code_string)
            return True
        except SyntaxError as e:
            print(f"[SHADOW TEST FAILED]: Syntax Error -> {e}")
            return False

    def create_backup(self, file_path: str):
        if os.path.exists(file_path):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = os.path.basename(file_path)
            backup_path = os.path.join(self.backup_dir, f"{file_name}.{timestamp}.bak")
            shutil.copy2(file_path, backup_path)
            return backup_path
        return None

    def evolve_file(self, target_file_path: str, directive: str) -> dict:
        full_path = os.path.join(self.base_dir, target_file_path)
        current_code = ""
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                current_code = f.read()

        system_prompt = (
            f"Modify or create '{target_file_path}'. Directive: {directive}. "
            f"Return ONLY raw Python code without markdown."
        )
        if current_code:
            system_prompt += f"\n\nCURRENT CODE:\n{current_code}"

        new_code = self.ai.generate(system_prompt)
        new_code = new_code.replace("```python\n", "").replace("```python", "").replace("```", "").strip()

        if not self.shadow_test_syntax(new_code):
            return {"status": "FAILED", "reason": "Syntax errors in generated code."}

        self.create_backup(full_path)
        os.makedirs(os.path.dirname(full_path) if os.path.dirname(full_path) else '.', exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_code)

        return {"status": "SUCCESS", "file_path": full_path}
      
