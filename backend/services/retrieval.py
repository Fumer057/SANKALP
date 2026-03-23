"""
Intelligent Retrieval Engine - Massive Scale Edition.

Queries the Sketchfab Global API for millions of real-world 3D models.
Uses a local SQLite database for persistent search caching.
"""
import httpx
from typing import Optional
from config import SKETCHFAB_API_KEY
from services.database import get_cached_search, save_search_cache, get_model_metadata, save_model_metadata

# --- Local Sample fallback for zero-connectivity/testing ---
MODEL_DATABASE = [
    {
        "id": "astronaut-001",
        "name": "Astronaut",
        "tags": ["space", "astronaut", "human", "suit", "nasa", "spaceman", "solar", "universe"],
        "category": "space",
        "url": "/static/models/astronaut.glb",
        "thumbnail": "",
        "source": "Local Asset (Google Model Viewer)",
        "poly_count": 15000,
        "file_size_mb": 2.7,
        "description": "A detailed NASA astronaut in a full EVA spacesuit.",
    }
]

async def retrieve_models(search_profile: dict, max_results: int = 4) -> list[dict]:
    """
    Search millions of models via Sketchfab API + Local Cache.
    Returns a ranked list of candidate models.
    """
    query = search_profile.get("core_entity", "").lower()
    
    # 1. Check SQLite Cache
    cached = get_cached_search(query)
    if cached:
        return cached[:max_results]

    # 2. Query Global Sketchfab API
    global_results = await search_sketchfab(search_profile, SKETCHFAB_API_KEY)
    
    # 3. Incorporate local results if highly relevant
    local_match = []
    for m in MODEL_DATABASE:
        if query in " ".join(m["tags"]).lower() or query in m["name"].lower():
            local_match.append({**m, "relevance_score": 100})
            
    all_results = local_match + global_results
    
    # 4. Save to Cache
    if all_results:
        save_search_cache(query, all_results)
        
    return all_results[:max_results]

async def search_sketchfab(search_profile: dict, api_key: str) -> list[dict]:
    """
    Direct integration with Sketchfab Global Catalog.
    Includes filtering to ensure results are actually semantically relevant.
    """
    if not api_key:
        return []

    query = search_profile.get("core_entity", "").lower()
    valid_terms = [t.lower() for t in search_profile.get("search_keywords", []) + [query]]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # We filter for downloadable AND glb compatible
            response = await client.get(
                "https://api.sketchfab.com/v3/search",
                params={
                    "type": "models",
                    "q": query,
                    "downloadable": "true",
                    "archives_flavors": "gltf", 
                    "sort_by": "-relevance",
                    "count": 24, # Fetch more to allow for filtering and diverse candidates
                },
                headers={"Authorization": f"Token {api_key}"},
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("results", []):
                    # Strict Accuracy Filter: The model's title or tags must contain the exact core entity
                    # or at least ALL the words of the core entity.
                    name = item.get("name", "").lower()
                    tags = [t.get("slug", "").replace("-", " ").lower() for t in item.get("tags", [])]
                    
                    query_words = query.split()
                    
                    is_exact_match = (query in name) or (query in tags)
                    is_all_words_match = all(word in name for word in query_words)
                    
                    if not (is_exact_match or is_all_words_match):
                        continue # Skip loosely related results
                        
                    results.append({
                        "id": item["uid"],
                        "name": item["name"],
                        "url": f"https://sketchfab.com/models/{item['uid']}/embed", 
                        "thumbnail": item.get("thumbnails", {}).get("images", [{}])[0].get("url", ""),
                        "source": "Sketchfab Global",
                        "description": item.get("description", "")[:200],
                        "poly_count": item.get("faceCount", 0),
                        "relevance_score": 100 if query in item["name"].lower() else 85,
                        "is_external": True
                    })
                return results
    except Exception as e:
        print(f"Sketchfab Search Error: {e}")
    
    return []
