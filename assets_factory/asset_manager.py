import os
import base64

class GodAssetForge:
    def __init__(self, base_dir="assets_factory"):
        # ऑटोमैटिक फोल्डर्स बनाना ताकि तुम्हें मैन्युअल रूप से कुछ न करना पड़े
        self.models_dir = os.path.join(base_dir, "3d_models")
        self.audio_dir = os.path.join(base_dir, "audio_sfx")
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)

    def save_3d_model(self, model_name: str, raw_code: str, extension: str = ".obj") -> str:
        """AI जनरेटेड 3D मॉडल कोड को असली 3D फाइल में कन्वर्ट करना"""
        file_path = os.path.join(self.models_dir, f"{model_name}{extension}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(raw_code)
        print(f"[ASSET FORGE]: 3D Model '{model_name}' forged successfully.")
        return file_path

    def save_audio_sfx(self, audio_name: str, base64_audio: str) -> str:
        """साउंड इफेक्ट्स को सेव करना (Base64 से डिकोड करके)"""
        file_path = os.path.join(self.audio_dir, f"{audio_name}.mp3")
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(base64_audio))
        print(f"[ASSET FORGE]: Audio SFX '{audio_name}' synthesized.")
        return file_path
      
