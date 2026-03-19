"""
Advanced AI Fallback Engine - High Fidelity Version.

Uses Meshy.ai for conceptually correct, game-ready 3D model generation.
"""
import httpx
import asyncio
import os
import time
from config import CONFIDENCE_THRESHOLD

MESHY_API_KEY = os.getenv("MESHY_API_KEY", "") # User needs to provide this

async def generate_fallback(search_profile: dict) -> dict:
    """
    Generate a high-fidelity 3D model via Meshy.ai.
    Focuses on conceptual correctness and clean geometry.
    """
    core_entity = search_profile.get("core_entity", "Unknown Concept")
    
    # If no API key, we return a "Pending" or "Mock" high-fidelity result
    if not MESHY_API_KEY:
        return {
            "id": f"gen-{int(time.time())}",
            "name": f"AI-Generated: {core_entity}",
            "url": "/static/models/box.glb",
            "source": "Meshy AI (Key Missing)",
            "description": "Please provide a MESHY_API_KEY to enable high-fidelity generation.",
            "is_fallback": True,
            "status": "error"
        }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Submit Text-to-3D Task
            headers = {"Authorization": f"Bearer {MESHY_API_KEY}"}
            payload = {
                "mode": "preview", # 'preview' is faster/cheap for prototypes
                "prompt": core_entity,
                "art_style": "realistic",
                "negative_prompt": "low quality, distorted, blobby, noisy"
            }
            
            response = await client.post(
                "https://api.meshy.ai/v1/text-to-3d",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 202:
                task_id = response.json().get("result")
                
                # 2. Poll for Completion (Max 60 seconds for preview)
                for _ in range(12): # Poll every 5s for 60s
                    await asyncio.sleep(5)
                    task_response = await client.get(
                        f"https://api.meshy.ai/v1/text-to-3d/{task_id}",
                        headers=headers
                    )
                    
                    if task_response.status_code == 200:
                        task_data = task_response.json()
                        if task_data.get("status") == "SUCCEEDED":
                            model_url = task_data.get("model_urls", {}).get("glb")
                            return {
                                "id": task_id,
                                "name": f"AI-Generated: {core_entity}",
                                "url": model_url,
                                "source": "Meshy AI (High Fidelity)",
                                "description": f"A conceptually correct 3D representation of '{core_entity}' generated via Meshy AI.",
                                "is_fallback": True,
                                "status": "success",
                                "poly_count": task_data.get("face_count", 0)
                            }
                        elif task_data.get("status") == "FAILED":
                            break
                            
    except Exception as e:
        print(f"Meshy AI Error: {e}")

    return {
        "id": "fallback-fail",
        "name": "Generation Failed",
        "url": "/static/models/box.glb",
        "source": "System Error",
        "description": "Failed to connect to High-Fidelity AI engine.",
        "is_fallback": True
    }
