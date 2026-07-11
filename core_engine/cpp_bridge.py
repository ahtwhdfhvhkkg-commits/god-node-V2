import os
import subprocess
import uuid

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
