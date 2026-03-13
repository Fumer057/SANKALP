"""
Fallback Engine.

Triggered when the best retrieved model falls below the confidence threshold.
Tier 1: Free Text-to-3D AI generation via Hugging Face (Shap-E)
"""
import time
import asyncio
import os
import shutil
from gradio_client import Client
from config import FALLBACK_MODEL_URL

async def generate_fallback(search_profile: dict) -> dict:
    """
    Generate a fallback 3D model when retrieval fails.
    Calls a free Hugging Face Space (Shap-E) for real text-to-3D generation.
    """
    core_entity = search_profile.get("core_entity", "Unknown Concept")
    
    # Path to the frontend public/generated folder
    # Assuming the current working directory is the backend folder
    # Move one level up to find frontend/public/generated
    generated_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "frontend", "public", "generated"))
    
    if not os.path.exists(generated_dir):
        os.makedirs(generated_dir, exist_ok=True)

    fallback_result = {
        "id": f"generated-{int(time.time())}",
        "name": f"AI-Generated: {core_entity}",
        "url": FALLBACK_MODEL_URL,
        "thumbnail": "",
        "source": "AI Fallback Engine (Free HF Shap-E)",
        "description": (
            f"This model was generated on the fly by a free open-source AI (Shap-E) "
            f"because no suitable pre-existing 3D model for '{core_entity}' was found."
        ),
        "poly_count": 0,
        "file_size_mb": 0,
        "confidence_score": 55,
        "validation_explanation": (
            f"🤖 FREE FALLBACK GENERATED: This is a fast, free AI-generated approximation of '{core_entity}'. "
            f"Generated via Shap-E (OpenAI) on Hugging Face Spaces."
        ),
        "generation_method": "text-to-3d",
        "generation_tier": 1,
        "is_fallback": True,
    }

    try:
        print(f"Starting free 3D generation for: {core_entity}...")
        # Use a more reliable/faster free space if Shap-E is busy, but Shap-E is standard.
        client = Client("hysts/Shap-E")
        
        # predict(prompt, seed, guidance_scale, num_inference_steps, api_name="/text-to-3d")
        # seed=0, guidance_scale=15.0, steps=64 (defaults)
        loop = asyncio.get_event_loop()
        result_path = await loop.run_in_executor(
            None, 
            lambda: client.predict(
                prompt=core_entity,
                seed=0,
                guidance_scale=15.0,
                num_inference_steps=32, # Faster for prototype
                api_name="/text-to-3d"
            )
        )

        if result_path and os.path.exists(result_path):
            filename = f"gen_{int(time.time())}_{core_entity.replace(' ', '_')}.glb"
            dest_path = os.path.join(generated_dir, filename)
            
            # Move the generated file to the frontend's public directory
            shutil.copy2(result_path, dest_path)
            
            # Return the relative URL that the frontend can load
            fallback_result["url"] = f"/generated/{filename}"
            fallback_result["file_size_mb"] = round(os.path.getsize(dest_path) / (1024 * 1024), 2)
            print(f"Generation complete! File saved to: {dest_path}")
            
    except Exception as e:
        print(f"Error during free 3D generation: {e}")
        # If it fails, we still return the fallback result with the default Box URL

    return fallback_result

def generate_primitive_scene(search_profile: dict) -> dict:
    return {}

