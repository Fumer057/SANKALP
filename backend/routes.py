from fastapi import APIRouter, Query, Request
from pydantic import BaseModel
from typing import Optional
import os

from services.query_processor import expand_query
from services.retrieval import retrieve_models
from services.validator import validate_and_score
from services.fallback import generate_fallback
from config import CONFIDENCE_THRESHOLD

router = APIRouter(prefix="/api", tags=["search"])

def resolve_url(url: str, request: Request) -> str:
    """Prepend the base URL to relative model paths."""
    if not url or url.startswith("http"):
        return url
    base_url = str(request.base_url).rstrip("/")
    clean_url = url if url.startswith("/static") else f"/static{url}"
    return f"{base_url}{clean_url}"

# --- Response Models ---
class SearchResponse(BaseModel):
    status: str
    query: str
    search_profile: dict
    pipeline_stages: list[dict]
    best_model: Optional[dict] = None
    all_candidates: list[dict] = []
    is_fallback: bool = False

@router.get("/search", response_model=SearchResponse)
async def search_3d_model(request: Request, q: str = Query(..., description="The concept to visualize in 3D")):
    pipeline_stages = []
    
    # --- Stage 1: Query Expansion ---
    search_profile = expand_query(q)
    pipeline_stages.append({
        "stage": 1, 
        "name": "Semantic Expansion", 
        "status": "completed", 
        "detail": f"Processed '{q}'. Identified core entity: '{search_profile['core_entity']}'."
    })

    # --- Stage 2: Global Global Retrieval (Sketchfab API) ---
    # Now searching millions of models directly
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
    
    is_fallback = False
    best_model = None

    # --- Stage 4: Result Selection or High-Fidelity Generation ---
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
            "name": "High-Fidelity AI Generation",
            "status": "completed",
            "detail": "No suitable global match found. Activating Meshy AI for conceptual generation."
        })
        best_model = await generate_fallback(search_profile)

    # Resolve URLs
    if best_model:
        best_model["url"] = resolve_url(best_model.get("url"), request)
    
    resolved_candidates = []
    for cand in scored_candidates:
        c = cand.copy()
        c["url"] = resolve_url(c.get("url"), request)
        resolved_candidates.append(c)

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
    base_static = os.path.join(os.path.dirname(__file__), "static")
    models_dir = os.path.join(base_static, "models")
    if os.path.exists(models_dir):
        for f in os.listdir(models_dir):
            if f.endswith(".glb"):
                output.append({
                    "id": f,
                    "name": f.replace(".glb", "").replace("_", " ").title(),
                    "url": resolve_url(f"/static/models/{f}", request),
                    "source": "Local System"
                })

    # 2. SQLite Cache (Recently Seen Global Models)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT results_json FROM search_cache LIMIT 50")
        for row in cursor.fetchall():
            models = json.loads(row[0])
            for m in models:
                m["url"] = resolve_url(m.get("url"), request)
                output.append(m)
        conn.close()
    except:
        pass
    
    return {"status": "success", "models": output}
