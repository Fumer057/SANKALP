"""
API Routes for the AI 3D Visualization System.
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

from services.query_processor import expand_query
from services.retrieval import retrieve_models
from services.validator import validate_and_score
from services.fallback import generate_fallback, generate_primitive_scene
from services.web_scraper import search_web_for_glb
from config import CONFIDENCE_THRESHOLD

router = APIRouter(prefix="/api", tags=["search"])


# --- Response Models ---
class SearchResponse(BaseModel):
    status: str
    query: str
    search_profile: dict
    pipeline_stages: list[dict]
    best_model: Optional[dict] = None
    all_candidates: list[dict] = []
    is_fallback: bool = False
    confidence_threshold: int = CONFIDENCE_THRESHOLD


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


# --- Endpoints ---

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="AI 3D Visualization System",
        version="0.1.0",
    )


@router.get("/search", response_model=SearchResponse)
async def search_3d_model(q: str = Query(..., description="The concept to visualize in 3D")):
    """
    Main search endpoint. Orchestrates the full pipeline:
    1. Query Expansion
    2. Local DB Retrieval
    3. AI Validation & Scoring
    4. Live Web Search (Sketchfab) — if local score too low
    5. AI Text-to-3D Generation (Shap-E) — only if web search also fails
    """
    pipeline_stages = []

    # --- Stage 1: Query Processing ---
    search_profile = expand_query(q)
    pipeline_stages.append({
        "stage": 1,
        "name": "Query Processing & Semantic Expansion",
        "status": "completed",
        "detail": f"Identified core entity: '{search_profile['core_entity']}' "
                  f"(Category: {search_profile['category']}). "
                  f"Generated {len(search_profile['search_keywords'])} search keywords "
                  f"and {len(search_profile['semantic_alternatives'])} alternatives.",
    })

    # --- Stage 2: Local Intelligent Retrieval ---
    candidates = retrieve_models(search_profile)
    pipeline_stages.append({
        "stage": 2,
        "name": "Intelligent Retrieval",
        "status": "completed",
        "detail": f"Found {len(candidates)} candidate models from the local database.",
    })

    # --- Stage 3: AI Validation ---
    scored_candidates = validate_and_score(candidates, search_profile)
    best_score = scored_candidates[0]["confidence_score"] if scored_candidates else 0
    pipeline_stages.append({
        "stage": 3,
        "name": "AI Validation & Scoring",
        "status": "completed",
        "detail": f"Validated {len(scored_candidates)} candidates. "
                  f"Best score: {best_score}% "
                  f"(Threshold: {CONFIDENCE_THRESHOLD}%).",
    })

    # --- Stage 4: Determine result, web search, or fallback ---
    is_fallback = False
    best_model = None

    if scored_candidates and best_score >= CONFIDENCE_THRESHOLD:
        # Local DB match is good enough — use it directly
        best_model = scored_candidates[0]
        pipeline_stages.append({
            "stage": 4,
            "name": "Result Selection",
            "status": "completed",
            "detail": f"Selected '{best_model['name']}' with {best_score}% confidence from local database. No web search needed.",
        })
    else:
        # Local match too weak — search the live web first
        pipeline_stages.append({
            "stage": 4,
            "name": "Live Web Search (Sketchfab)",
            "status": "completed",
            "detail": f"Local confidence {best_score}% is below threshold {CONFIDENCE_THRESHOLD}%. "
                      f"Searching Sketchfab's catalog for a real 3D model of '{search_profile['core_entity']}'...",
        })

        web_model = await search_web_for_glb(search_profile["core_entity"])

        if web_model:
            best_model = web_model
            pipeline_stages.append({
                "stage": 5,
                "name": "Web Model Retrieved",
                "status": "completed",
                "detail": f"Found and downloaded a real 3D model from Sketchfab for '{search_profile['core_entity']}'. Cached locally.",
            })
        else:
            # Web search also failed — generate with Shap-E as last resort
            is_fallback = True
            fallback_model = await generate_fallback(search_profile)
            best_model = fallback_model
            pipeline_stages.append({
                "stage": 5,
                "name": "AI Generation (Shap-E)",
                "status": "completed",
                "detail": f"No matching 3D model found on the web. "
                          f"Generating a new model for '{search_profile['core_entity']}' using Shap-E AI.",
            })

    return SearchResponse(
        status="success",
        query=q,
        search_profile=search_profile,
        pipeline_stages=pipeline_stages,
        best_model=best_model,
        all_candidates=scored_candidates,
        is_fallback=is_fallback,
        confidence_threshold=CONFIDENCE_THRESHOLD,
    )


@router.get("/models")
async def list_available_models():
    """List all models in the local database."""
    from services.retrieval import MODEL_DATABASE
    return {
        "status": "success",
        "count": len(MODEL_DATABASE),
        "models": MODEL_DATABASE,
    }


@router.get("/gallery")
async def get_gallery_models():
    """Scan local directories for all downloaded/cached 3D models."""
    import os
    frontend_public = os.path.abspath(os.path.join(os.getcwd(), "..", "frontend", "public"))
    models_dir = os.path.join(frontend_public, "models")
    generated_dir = os.path.join(frontend_public, "generated")
    
    gallery = []
    
    # Static models
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith(".glb") and file != "box.glb":
                path = os.path.join(models_dir, file)
                size_mb = os.path.getsize(path) / (1024 * 1024)
                name = file.replace(".glb", "").replace("_", " ").title()
                gallery.append({
                    "id": f"static-{file}",
                    "name": name,
                    "url": f"/models/{file}",
                    "source": "Local System Database",
                    "file_size_mb": round(size_mb, 2)
                })
                
    # Web Scraped / Generated models
    if os.path.exists(generated_dir):
        from services.web_scraper import GLB_CATALOG, _cache_key
        for file in os.listdir(generated_dir):
            if file.endswith(".glb"):
                path = os.path.join(generated_dir, file)
                size_mb = os.path.getsize(path) / (1024 * 1024)
                
                name = "Web Scraped Model"
                source = "Web Retrieved (CDN Cache)" if "cat_" in file else "AI Generated (Shap-E)"
                
                for item in GLB_CATALOG:
                    if _cache_key(item["url"]) in file:
                        name = item["name"]
                        break
                        
                gallery.append({
                    "id": f"web-{file}",
                    "name": name,
                    "url": f"/generated/{file}",
                    "source": source,
                    "file_size_mb": round(size_mb, 2)
                })
                
    return {
        "status": "success",
        "count": len(gallery),
        "models": gallery
    }
