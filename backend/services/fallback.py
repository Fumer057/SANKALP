"""
Advanced AI Fallback Engine - Next-Gen TRELLIS Pipeline.

Tiers:
1. High Fidelity: Pollinations (Image) -> TRELLIS (Advanced 3D) - BEST QUALITY
2. High Stability: Shap-E (Direct 3D)
3. Failsafe: Conceptual Match from Corrected Local Cache
"""
import os
import time
import asyncio
import shutil
import trimesh
import random
import httpx
from gradio_client import Client
from config import CONFIDENCE_THRESHOLD, SAMPLE_MODELS

# --- Global Client Cache ---
_CLIENT_CACHE = {}

# The HF_TOKEN must be set in the Render environment variables for high-fidelity generation.
HF_TOKEN = os.getenv("HF_TOKEN", None)

def get_trellis_client():
    if "trellis" not in _CLIENT_CACHE:
        try:
            print("Connecting to Next-Gen TRELLIS Space...")
            _CLIENT_CACHE["trellis"] = Client("JeffreyXiang/TRELLIS", hf_token=HF_TOKEN)
        except Exception as e:
            print(f"      [Connection Failed] TRELLIS: {e}")
            return None
    return _CLIENT_CACHE["trellis"]

def get_shape_client():
    if "shape" not in _CLIENT_CACHE:
        try:
            _CLIENT_CACHE["shape"] = Client("hysts/Shap-E", hf_token=HF_TOKEN)
        except:
            return None
    return _CLIENT_CACHE["shape"]

async def generate_fallback(search_profile: dict) -> dict:
    core_entity = search_profile.get("core_entity", "Unknown Concept")
    base_static = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
    generated_dir = os.path.join(base_static, "generated")
    os.makedirs(generated_dir, exist_ok=True)
    
    loop = asyncio.get_event_loop()
    filename = f"gen_{int(time.time())}.glb"
    dest_path = os.path.join(generated_dir, filename)

    print(f"\n--- Initiating Next-Gen AI Generation for '{core_entity}' ---")

    # =========================================================================
    # TIER 1: HIGH FIDELITY (Pollinations -> TRELLIS)
    # =========================================================================
    t1_error = "None"
    try:
        print("[Tier 1] Generating Image (Pollinations.ai)...")
        image_url = f"https://image.pollinations.ai/prompt/A%20single%20high%20quality%203D%20render%20of%20a%20{core_entity.replace(' ', '%20')}%20isolated%20on%20white%20background%20detailed?width=1024&height=1024&nologo=true"
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(image_url, timeout=10)
            if resp.status_code == 200:
                temp_image = os.path.join(generated_dir, f"base_{int(time.time())}.jpg")
                with open(temp_image, "wb") as f:
                    f.write(resp.content)
                
                print("[Tier 1] Image Ready. Connecting to TRELLIS...")
                trellis = await loop.run_in_executor(None, get_trellis_client)
                
                if trellis:
                    try:
                        print("      [Stage 1/2] Generating Latent Representation...")
                        asset_v_path = await loop.run_in_executor(
                            None,
                            lambda: trellis.predict(
                                image=temp_image, 
                                multiimages=[], 
                                seed=random.randint(0, 1000), 
                                ss_guidance_strength=7.5,
                                ss_sampling_steps=12,
                                slat_guidance_strength=3.0,
                                slat_sampling_steps=12,
                                multiimage_algo="stochastic",
                                api_name="/image_to_3d"
                            )
                        )
                        
                        print("      [Stage 2/2] Extracting GLB mesh...")
                        extracted_paths = await loop.run_in_executor(
                            None,
                            lambda: trellis.predict(
                                mesh_simplify=0.95,
                                texture_size=1024,
                                api_name="/extract_glb"
                            )
                        )
                        
                        glb_temp_path = extracted_paths[1]
                        shutil.copy2(glb_temp_path, dest_path)
                        
                        return {
                            "id": f"gen-t1-{int(time.time())}",
                            "name": f"AI-Generated: {core_entity}",
                            "url": f"/static/generated/{filename}",
                            "source": "TRELLIS (Next-Gen AI)",
                            "description": f"State-of-the-art 3D reconstruction of '{core_entity}' generated using the TRELLIS pipeline. Superior geometric accuracy and detail.",
                            "file_size_mb": round(os.path.getsize(dest_path) / (1024 * 1024), 2),
                            "status": "success",
                            "is_fallback": True
                        }
                    except Exception as e_inner:
                        t1_error = str(e_inner)[:100]
                        print(f"      [TRELLIS Generation Failed] {t1_error}")
    except Exception as e_base:
        t1_error = str(e_base)[:100]

    # =========================================================================
    # TIER 2: HIGH STABILITY (Shap-E)
    # =========================================================================
    t2_error = "None"
    try:
        print("[Tier 2] Falling back to Shap-E Stability Pipeline...")
        shape = await loop.run_in_executor(None, get_shape_client)
        if shape:
            glb_path = await loop.run_in_executor(
                None,
                lambda: shape.predict(
                    prompt=f"A 3D model of a {core_entity}",
                    seed=0, guidance_scale=15.0, num_inference_steps=64, api_name="/text-to-3d"
                )
            )
            shutil.copy2(glb_path, dest_path)
            return {
                "id": f"gen-t2-{int(time.time())}",
                "name": f"AI-Generated: {core_entity}",
                "url": f"/static/generated/{filename}",
                "source": "Shap-E (Tier 2 AI)",
                "description": f"3D representation generated using Shap-E stability backup.",
                "file_size_mb": round(os.path.getsize(dest_path) / (1024 * 1024), 2),
                "status": "success",
                "is_fallback": True
            }
    except Exception as e_shape:
        t2_error = str(e_shape)[:100]

    # =========================================================================
    # TIER 3: CONCEPTUAL SMART-MATCH (Cache)
    # =========================================================================
    print("[Tier 3] Serving Conceptual Backup Asset.")
    safe_model = SAMPLE_MODELS.get("solar_system")
    for key, model in SAMPLE_MODELS.items():
        if key in core_entity.lower() or core_entity.lower() in key:
            safe_model = model
            break
            
    return {
        "id": "gen-t3-fallback",
        "name": f"{safe_model['name']} (Concept Match)",
        "url": safe_model["url"],
        "source": "SANKALP System Cache",
        "description": f"AI Generation skipped or failed. Logs: T1:{t1_error} | T2:{t2_error}. Showing conceptual match.",
        "file_size_mb": 2.5,
        "status": "success",
        "is_fallback": True
    }
