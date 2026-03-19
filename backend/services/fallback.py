"""
Advanced AI Fallback Engine - High Reliability Version (100% Free).

Uses the highly stable `hysts/Shap-E` Hugging Face Space for direct Text-to-3D.
"""
import os
import time
import asyncio
import shutil
from gradio_client import Client
from config import CONFIDENCE_THRESHOLD

async def generate_fallback(search_profile: dict) -> dict:
    """
    Generate a 3D model using a fully open-source reliable Text-to-3D pipeline (Shap-E).
    """
    core_entity = search_profile.get("core_entity", "Unknown Concept")
    
    # Path to the frontend public/generated folder
    base_static = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
    generated_dir = os.path.join(base_static, "generated")
    os.makedirs(generated_dir, exist_ok=True)
    
    fallback_result = {
        "id": f"gen-fail",
        "name": f"Generation Failed",
        "url": "/static/models/box.glb",
        "source": "System Error",
        "description": "Failed to connect to Hugging Face free AI engines. Overloaded.",
        "is_fallback": True,
        "status": "error"
    }

    try:
        print(f"Starting reliable Text-to-3D generation for: '{core_entity}'...")
        loop = asyncio.get_event_loop()
        
        # --- Step 1: Text-to-3D (Shap-E) ---
        print("[1/1] Generating 3D GLB directly with Shap-E...")
        
        def run_shape():
            client = Client("hysts/Shap-E")
            return client.predict(
                prompt=f"A highly detailed 3D model of a {core_entity}",
                seed=0,
                guidance_scale=15.0,
                num_inference_steps=64,
                api_name="/text-to-3d"
            )
            
        glb_path = await loop.run_in_executor(None, run_shape)
        print(f"      3D GLB generated successfully at {glb_path}")

        # --- Step 2: Move locally ---
        filename = f"gen_{int(time.time())}.glb"
        dest_path = os.path.join(generated_dir, filename)
        
        shutil.copy2(glb_path, dest_path)
        print(f"      GLB saved successfully to {dest_path}")
        
        # Calculate size and update success response
        file_size_mb = round(os.path.getsize(dest_path) / (1024 * 1024), 2)
        
        fallback_result.update({
            "id": f"gen-{int(time.time())}",
            "name": f"AI-Generated: {core_entity}",
            "url": f"/static/generated/{filename}",
            "source": "Shap-E (Highly Stable Open-Source AI)",
            "description": f"A generated 3D representation of '{core_entity}' using OpenAI's Shap-E model. Deployed as a reliable fallback during high-traffic outages.",
            "file_size_mb": file_size_mb,
            "status": "success",
            "is_fallback": True
        })
        
    except Exception as e:
        print(f"Pipeline Error: {e}")

    return fallback_result
