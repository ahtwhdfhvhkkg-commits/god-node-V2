"""
core_engine/cpp_bridge.py

This module contains the C++ execution engine and the adapter 
that connects it directly to the simulation_scheduler.
"""

import os
import subprocess
import uuid
import json
from typing import Any, Dict, List

# 1. हमारी नई बनी हुई शेड्यूलर फाइलों से इम्पोर्ट (यह है असली वायरिंग)
from simulation_scheduler.adapters import ExecutionBackendAdapter
from simulation_scheduler.types import Batch

class CPPExecutionBridge:
    def __init__(self, workspace_dir="workspace_cpp"):
        # यह वो फोल्डर है जहाँ C++ कोड कुछ सेकंड के लिए बनेगा और रन होगा
        self.workspace = workspace_dir
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)

    def compile_and_run(self, cpp_code: str, execution_timeout: int = 15) -> dict:
        """
        यह फंक्शन C++ कोड को लेता है, उसे कंपाइल करता है और मैक्सिमम स्पीड (-O3) पर रन करता है।
        अगर कोई इनफिनिट लूप (Infinite loop) हुआ, तो यह सर्वर को बचाने के लिए उसे टाइमआउट कर देगा।
        """
        # 1. हर टास्क के लिए एक यूनिक ID बनाना (ताकि मल्टीप्लेयर में कोड आपस में न टकराएं)
        job_id = str(uuid.uuid4())[:8]
        cpp_file = os.path.join(self.workspace, f"render_task_{job_id}.cpp")
        
        # Windows (.exe) और Linux (.out) दोनों क्लाउड सर्वर्स के लिए सपोर्ट
        exe_ext = ".exe" if os.name == 'nt' else ".out"
        exe_file = os.path.join(self.workspace, f"task_{job_id}{exe_ext}")

        # 2. C++ कोड को फाइल में लिखना
        with open(cpp_file, "w", encoding="utf-8") as f:
            f.write(cpp_code)

        try:
            # 3. C++ कोड को कंपाइल करना (g++ कंपाइलर का उपयोग करके, -O3 से अल्ट्रा-फास्ट स्पीड मिलेगी)
            compile_process = subprocess.run(
                ["g++", "-O3", cpp_file, "-o", exe_file],
                capture_output=True,
                text=True,
                timeout=20
            )
            
            # अगर C++ कोड में कोई सिंटैक्स एरर है
            if compile_process.returncode != 0:
                return {
                    "status": "COMPILATION_ERROR",
                    "logs": compile_process.stderr
                }

            # 4. कंपाइल हुई .exe या .out फाइल को रन करना
            run_command = [f"./{exe_file}"] if os.name != 'nt' else [exe_file]
            run_process = subprocess.run(
                run_command,
                capture_output=True,
                text=True,
                timeout=execution_timeout
            )

            return {
                "status": "SUCCESS",
                "output": run_process.stdout,
                "errors": run_process.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "TIMEOUT", 
                "logs": "Execution exceeded time limit. Engine halted infinite loop to protect server."
            }
        except Exception as e:
            return {
                "status": "FATAL_BRIDGE_ERROR", 
                "logs": str(e)
            }
        finally:
            # 5. ऑटो-क्लीनअप (सर्वर की मेमोरी बचाने के लिए इस्तेमाल के तुरंत बाद कचरा हटाना)
            if os.path.exists(cpp_file): 
                os.remove(cpp_file)
            if os.path.exists(exe_file): 
                os.remove(exe_file)


# =====================================================================
# THE WIRING: यह वो क्लास है जो तुम्हारे शेड्यूलर और C++ ब्रिज को जोड़ेगी
# =====================================================================

class SimulationCPPAdapter(ExecutionBackendAdapter):
    """
    यह प्लग (Adapter) simulation_scheduler से 'Batch' लेगा, 
    उसे C++ कोड में बदलेगा (या टास्क डेटा पास करेगा), 
    और CPPExecutionBridge के जरिए सुपर-फास्ट रन करेगा।
    """
    
    def __init__(self, workspace_dir="workspace_cpp"):
        # शेड्यूलर शुरू होते ही यह C++ इंजन को बैकग्राउंड में ऑन कर देगा
        self.bridge = CPPExecutionBridge(workspace_dir)

    def execute(self, batch: Batch) -> Any:
        """
        यह फंक्शन शेड्यूलर के 'executor.py' द्वारा अपने आप बुलाया जाएगा।
        """
        results = []
        
        # बैच के अंदर जितने भी टास्क्स (Tasks) हैं, उन पर लूप चलाना
        for task in batch.tasks:
            
            # (भविष्य का लॉजिक) यहाँ हम टास्क के पेलोड के हिसाब से C++ कोड जनरेट करेंगे।
            # अभी के लिए एक डमी C++ कोड जो दिखाएगा कि कनेक्शन हो गया है:
            cpp_code_to_run = f"""
            #include <iostream>
            #include <string>
            using namespace std;
            
            int main() {{
                cout << "{{" << "\\\"task_id\\\": \\\"" << "{task.task_id}" << "\\\", "
                     << "\\\"status\\\": \\\"executed_in_cpp\\\"" << "}}" << endl;
                return 0;
            }}
            """
            
            # C++ ब्रिज को कोड देना और रन करवाना
            execution_result = self.bridge.compile_and_run(
                cpp_code=cpp_code_to_run,
                execution_timeout=15
            )
            
            # रिज़ल्ट को सेव करना
            results.append({
                "task_id": task.task_id,
                "engine_response": execution_result
            })
            
        # शेड्यूलर को वापस रिजल्ट भेज देना ताकि वो मेमोरी में सेव (Cache) कर सके
        return results

