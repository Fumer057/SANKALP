from fastapi import APIRouter, Query, Request
from pydantic import BaseModel
from typing import Optional
import os

from services.query_processor import expand_query
from services.retrieval import retrieve_models
from services.validator import validate_and_score
from services.fallback import generate_fallback
from services.web_scraper import search_web_for_glb
from config import CONFIDENCE_THRESHOLD

router = APIRouter(prefix="/api", tags=["search"])

def resolve_url(url: str, request: Request) -> str:
    """Prepend the base URL to relative model paths."""
    if not url or url.startswith("http"):
        return url
    base_url = str(request.base_url).rstrip("/")
    # Force /static/ prefix if missing to align with our FastAPI mount
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
    search_profile = expand_query(q)
    pipeline_stages.append({
        "stage": 1, "name": "Query Processing", "status": "completed", 
        "detail": f"Identified: '{search_profile['core_entity']}'"
    })

    candidates = retrieve_models(search_profile)
    scored_candidates = validate_and_score(candidates, search_profile)
    best_score = scored_candidates[0]["confidence_score"] if scored_candidates else 0
    
    is_fallback = False
    best_model = None

    if scored_candidates and best_score >= CONFIDENCE_THRESHOLD:
        best_model = scored_candidates[0].copy()
    else:
        web_model = await search_web_for_glb(search_profile["core_entity"])
        if web_model:
            best_model = web_model.copy()
        else:
            is_fallback = True
            best_model = await generate_fallback(search_profile)

    # Resolve URLs to absolute addresses
    if best_model:
        best_model["url"] = resolve_url(best_model["url"], request)
    
    resolved_candidates = []
    for cand in scored_candidates:
        c = cand.copy()
        c["url"] = resolve_url(c["url"], request)
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
    """Scan backend/static/ and return models with absolute URLs."""
    base_static = os.path.join(os.path.dirname(__file__), "static")
    models_dir = os.path.join(base_static, "models")
    gen_dir = os.path.join(base_static, "generated")
    
    output = []
    
    paths = [(models_dir, "models", "Local"), (gen_dir, "generated", "Generated")]
    
    for directory, sub_path, label in paths:
        if os.path.exists(directory):
            for f in os.listdir(directory):
                if f.endswith(".glb"):
                    rel_url = f"/static/{sub_path}/{f}"
                    output.append({
                        "id": f,
                        "name": f.replace(".glb", "").replace("_", " ").title(),
                        "url": resolve_url(rel_url, request),
                        "source": label,
                        "file_size_mb": round(os.path.getsize(os.path.join(directory, f)) / (1024 * 1024), 2)
                    })
    
    return {"status": "success", "models": output}

@router.get("/models")
async def list_models():
    """Fallback for old endpoints."""
    from services.retrieval import MODEL_DATABASE
    return {"status": "success", "models": MODEL_DATABASE}
