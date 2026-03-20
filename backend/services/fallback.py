"""
AI Fallback Engine - Streamlined Shap-E Core.

Uses the highly stable `hysts/Shap-E` Hugging Face Space for direct Text-to-3D.
"""
import os
import time
import asyncio
import shutil
from gradio_client import Client
from config import SAMPLE_MODELS

# --- Global Client Cache ---
_CLIENT_CACHE = {"shape": None}
HF_TOKEN = os.getenv("HF_TOKEN", None)

def get_shape_client():
    if not _CLIENT_CACHE["shape"]:
        try:
            print("Initializing Reliable Shap-E Client...")
            _CLIENT_CACHE["shape"] = Client("hysts/Shap-E", hf_token=HF_TOKEN)
        except Exception as e:
            print(f"Shap-E Init Error: {e}")
            return None
    return _CLIENT_CACHE["shape"]

async def generate_fallback(search_profile: dict) -> dict:
    """
    Generate a 3D model using the streamlined Shap-E pipeline.
    """
    core_entity = search_profile.get("core_entity", "Unknown Concept")
    base_static = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
    generated_dir = os.path.join(base_static, "generated")
    os.makedirs(generated_dir, exist_ok=True)
    
    loop = asyncio.get_event_loop()
    filename = f"gen_{int(time.time())}.glb"
    dest_path = os.path.join(generated_dir, filename)

    print(f"\n--- Initiating Shap-E Generation for '{core_entity}' ---")

    try:
        shape = await loop.run_in_executor(None, get_shape_client)
        if shape:
            print(f"[Shap-E] Generating 3D GLB directly for: {core_entity}...")
            glb_path = await loop.run_in_executor(
                None,
                lambda: shape.predict(
                    prompt=f"A high quality 3D model of a {core_entity}",
                    seed=0, guidance_scale=15.0, num_inference_steps=64, api_name="/text-to-3d"
                )
            )
            shutil.copy2(glb_path, dest_path)
            
            return {
                "id": f"gen-shape-{int(time.time())}",
                "name": f"AI-Generated: {core_entity}",
                "url": f"/static/generated/{filename}",
                "source": "Shap-E (Reliable AI)",
                "description": f"A generated 3D representation of '{core_entity}' using OpenAI's Shap-E model. Simplified for high reliability.",
                "file_size_mb": round(os.path.getsize(dest_path) / (1024 * 1024), 2),
                "status": "success",
                "is_fallback": True
            }
    except Exception as e:
        print(f"[Shap-E] Failed: {e}")

    # Final Failsafe: Conceptual Match
    print("[Failsafe] Serving Conceptual Backup Asset.")
    safe_model = SAMPLE_MODELS.get("solar_system")
    for key, model in SAMPLE_MODELS.items():
        if key in core_entity.lower() or core_entity.lower() in key:
            safe_model = model
            break
            
    return {
        "id": "gen-failsafe",
        "name": f"{safe_model['name']} (Concept Match)",
        "url": safe_model["url"],
        "source": "SANKALP System Cache",
        "description": f"Shap-E AI services are currently overloaded. Showing context-matched conceptual model.",
        "file_size_mb": 2.5,
        "status": "success",
        "is_fallback": True
    }
