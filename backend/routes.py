from fastapi import APIRouter, Query, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os

from services.query_processor import expand_query
from services.retrieval import retrieve_models
from services.validator import validate_and_score
from services.fallback import generate_fallback
from config import CONFIDENCE_THRESHOLD

router = APIRouter(prefix="/api", tags=["search"])

def resolve_url(url: str, request: Request) -> str:
    """Prepend the base URL and force HTTPS if in production."""
    if not url:
        return url
    if url.startswith("http"):
        # Force HTTPS for cross-origin stability if it's a Render URL
        if "render.com" in url:
            return url.replace("http://", "https://")
        return url
        
    base_url = str(request.base_url).rstrip("/")
    # Force HTTPS for Render production environments
    if "render.com" in base_url:
        base_url = base_url.replace("http://", "https://")
        
    clean_url = url if url.startswith("/static") else f"/static{url}"
    return f"{base_url}{clean_url}"

# --- Response Models ---
class SearchResponse(BaseModel):
    status: str
    query: str
    search_profile: dict
    pipeline_stages: List[Dict[str, Any]]
    best_model: Optional[Dict[str, Any]] = None
    all_candidates: List[Dict[str, Any]] = []
    is_fallback: bool = False

@router.get("/search", response_model=SearchResponse)
async def search_3d_model(
    request: Request, 
    q: str = Query(..., description="The concept to visualize in 3D"),
    force_generate: bool = Query(False, description="Skip retrieval and force AI generation")
):
    pipeline_stages = []
    
    # --- Stage 1: Query Expansion ---
    search_profile = expand_query(q)
    pipeline_stages.append({
        "stage": 1, 
        "name": "Semantic Expansion", 
        "status": "completed", 
        "detail": f"Processed '{q}'. Identified core entity: '{search_profile['core_entity']}'."
    })

    scored_candidates = []
    best_score = 0
    is_fallback = False
    best_model = None

    if force_generate:
        pipeline_stages.append({
            "stage": 2,
            "name": "Global Retrieval bypassed",
            "status": "completed",
            "detail": "User forced AI generation. Skipping Sketchfab search."
        })
        pipeline_stages.append({
            "stage": 3,
            "name": "AI Validation bypassed",
            "status": "completed",
            "detail": "Skipping validation."
        })
        pipeline_stages.append({
            "stage": 4,
            "name": "AI 3D Generation (Forced)",
            "status": "completed",
            "detail": "Activating the highly reliable Shap-E AI Generation engine as requested."
        })
        is_fallback = True
        best_model = await generate_fallback(search_profile)
    else:
        # --- Stage 2: Global Retrieval (Sketchfab API) ---
        candidates = await retrieve_models(search_profile)
        pipeline_stages.append({
            "stage": 2,
            "name": "Global Retrieval",
            "status": "completed",
            "detail": f"Queried Sketchfab Global Index. Found {len(candidates)} matching 3D models."
        })

        # --- Stage 3: AI Validation ---
        scored_candidates = validate_and_score(candidates, search_profile)
        best_score = scored_candidates[0]["confidence_score"] if scored_candidates else 0
        pipeline_stages.append({
            "stage": 3,
            "name": "AI Validation",
            "status": "completed",
            "detail": f"Best match confidence: {best_score}% (Threshold: {CONFIDENCE_THRESHOLD}%)."
        })

        # --- Stage 4: Result Selection or AI Generation ---
        if scored_candidates and best_score >= CONFIDENCE_THRESHOLD:
            best_model = scored_candidates[0].copy()
            pipeline_stages.append({
                "stage": 4,
                "name": "Asset Selection",
                "status": "completed",
                "detail": f"Linking to global asset '{best_model['name']}' ({best_model['source']})."
            })
        else:
            is_fallback = True
            pipeline_stages.append({
                "stage": 4,
                "name": "AI 3D Generation",
                "status": "completed",
                "detail": "No suitable global match found. Activating reliable Shap-E AI Generation engine."
            })
            best_model = await generate_fallback(search_profile)

    # --- FINAL SCHEMA LOCKDOWN (Mandatory Fields for Frontend) ---
    def finalize_model(m: Dict[str, Any]) -> Dict[str, Any]:
        if not m: return m
        # Mandatory fields for Frontend interfaces
        m["id"] = m.get("id", "unnamed")
        m["name"] = m.get("name", "Unknown Model")
        m["url"] = resolve_url(m.get("url"), request)
        m["description"] = m.get("description", "A 3D representation of the queried concept.")
        m["source"] = m.get("source", "SANKALP Pipeline")
        m["file_size_mb"] = m.get("file_size_mb", 2.5)
        m["confidence_score"] = m.get("confidence_score", 0)
        m["validation_explanation"] = m.get("validation_explanation", "Automatic validation performed by AI pipeline.")
        return m

    if best_model:
        best_model = finalize_model(best_model)
    
    resolved_candidates = []
    for cand in scored_candidates:
        resolved_candidates.append(finalize_model(cand.copy()))

    return SearchResponse(
        status="success",
        query=q,
        search_profile=search_profile,
        pipeline_stages=pipeline_stages,
        best_model=best_model,
        all_candidates=resolved_candidates,
        is_fallback=is_fallback
    )

@router.get("/gallery")
async def get_gallery(request: Request):
    """Scan local storage and DB cache for all known models."""
    from services.database import DB_PATH
    import sqlite3
    import json
    
    output = []
    
    # 1. Local Files
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(BASE_DIR, "static", "models")
    if os.path.exists(models_dir):
        for f in os.listdir(models_dir):
            if f.endswith(".glb"):
                output.append({
                    "id": f,
                    "name": f.replace(".glb", "").replace("_", " ").title(),
                    "url": resolve_url(f"/static/models/{f}", request),
                    "source": "Local System",
                    "file_size_mb": 2.5 
                })

    # 2. SQLite Cache
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT results_json FROM search_cache LIMIT 50")
        for row in cursor.fetchall():
            models = json.loads(row[0])
            for m in models:
                m["url"] = resolve_url(m.get("url"), request)
                m["file_size_mb"] = m.get("file_size_mb", 2.5) 
                output.append(m)
        conn.close()
    except:
        pass
    
    return {"status": "success", "models": output}
