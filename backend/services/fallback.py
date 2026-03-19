"""
Advanced AI Fallback Engine - Open Source 2-Step Pipeline (100% Free).

Uses Hugging Face Spaces:
1. FLUX.1-schnell (Text-to-Image)
2. TripoSR (Image-to-3D)
"""
import os
import time
import asyncio
import shutil
import trimesh
from gradio_client import Client
from config import CONFIDENCE_THRESHOLD

async def generate_fallback(search_profile: dict) -> dict:
    """
    Generate a high-fidelity 3D model using a free 2-step open-source pipeline:
    Text -> FLUX.1 Image -> TripoSR 3D OBJ -> Trimesh GLB.
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
        "description": "Failed to connect to Hugging Face free AI engines.",
        "is_fallback": True,
        "status": "error"
    }

    try:
        print(f"Starting free 2-step 3D generation for: '{core_entity}'...")
        loop = asyncio.get_event_loop()
        
        # --- Step 1: Text-to-Image (FLUX.1-schnell) ---
        print("[1/2] Generating high-quality base image with FLUX.1...")
        flux_client = Client("black-forest-labs/FLUX.1-schnell")
        
        # Format the prompt to get a clean, isolated object suitable for 3D conversion
        image_prompt = f"A single high quality 3D render of a {core_entity}, isolated on a pure white background, extremely detailed, professional lighting, centered, full body."
        
        flux_output = await loop.run_in_executor(
            None,
            lambda: flux_client.predict(
                prompt=image_prompt,
                seed=0,
                randomize_seed=True,
                width=1024,
                height=1024,
                num_inference_steps=4,
                api_name="/infer"
            )
        )
        # flux_output returns (image_path, seed)
        image_path = flux_output[0]
        print(f"      Image generated successfully at {image_path}")

        # --- Step 2: Image-to-3D (TripoSR) ---
        print("[2/2] Converting 2D image to 3D geometry with TripoSR...")
        tripo_client = Client("stabilityai/TripoSR")
        
        tripo_output = await loop.run_in_executor(
            None,
            lambda: tripo_client.predict(
                image=image_path,
                foreground_ratio=0.85,
                mc_resolution=256,
                api_name="/process"
            )
        )
        obj_path = tripo_output # Returns a file path to a .obj
        print(f"      3D OBJ generated successfully at {obj_path}")
        
        # --- Step 3: Convert OBJ to GLB ---
        print("[3/3] Converting .obj to .glb format for web rendering...")
        filename = f"gen_{int(time.time())}.glb"
        dest_path = os.path.join(generated_dir, filename)
        
        def convert_to_glb():
            scene = trimesh.load(obj_path, force="mesh")
            scene.export(dest_path)
            
        await loop.run_in_executor(None, convert_to_glb)
        print(f"      GLB saved successfully to {dest_path}")
        
        # Calculate size and update success response
        file_size_mb = round(os.path.getsize(dest_path) / (1024 * 1024), 2)
        
        fallback_result.update({
            "id": f"gen-{int(time.time())}",
            "name": f"AI-Generated: {core_entity}",
            "url": f"/static/generated/{filename}",
            "source": "TripoSR (Free Open-Source AI)",
            "description": f"A conceptually correct 3D representation of '{core_entity}' generated using a free 2-step AI pipeline (FLUX.1 + TripoSR).",
            "file_size_mb": file_size_mb,
            "poly_count": len(trimesh.load(dest_path, force="mesh").faces),
            "status": "success",
            "is_fallback": True
        })
        
    except Exception as e:
        print(f"Pipeline Error: {e}")

    return fallback_result
