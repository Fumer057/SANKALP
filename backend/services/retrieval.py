"""
Intelligent Retrieval Engine.

Queries 3D model databases and returns candidate models.
In production, this would call the Sketchfab API and use a vector DB cache.
For the prototype, we use a curated set of free .glb models.
"""
import httpx
from typing import Optional


# --- Curated LOCAL GLB models (all hosted in frontend/public/models/) ---
MODEL_DATABASE = [
    {
        "id": "astronaut-001",
        "name": "Astronaut",
        "tags": ["space", "astronaut", "human", "suit", "nasa", "spaceman", "solar", "universe"],
        "category": "space",
        "url": "/models/astronaut.glb",
        "thumbnail": "",
        "source": "Local Asset (Google Model Viewer)",
        "poly_count": 15000,
        "file_size_mb": 2.7,
        "description": "A detailed NASA astronaut in a full EVA spacesuit, ready for a spacewalk.",
    },
    {
        "id": "horse-002",
        "name": "Horse",
        "tags": ["animal", "horse", "mammal", "biology", "anatomy", "creature", "wildlife"],
        "category": "biology",
        "url": "/models/horse.glb",
        "thumbnail": "",
        "source": "Local Asset (Three.js Samples)",
        "poly_count": 6000,
        "file_size_mb": 0.17,
        "description": "A realistic animated horse model.",
    },
    {
        "id": "robot-003",
        "name": "Robot Expressive",
        "tags": ["robot", "mechanical", "engine", "technology", "ai", "machine", "car", "motor", "vehicle", "android"],
        "category": "mechanical",
        "url": "/models/robot.glb",
        "thumbnail": "",
        "source": "Local Asset (Google Model Viewer)",
        "poly_count": 8000,
        "file_size_mb": 0.45,
        "description": "An expressive robot with articulated joints and mechanical components.",
    },
    {
        "id": "helmet-004",
        "name": "Battle Helmet",
        "tags": ["helmet", "head", "brain", "anatomy", "neural", "military", "armor", "scifi", "skull", "cranium", "neuroscience"],
        "category": "anatomy",
        "url": "/models/helmet.glb",
        "thumbnail": "",
        "source": "Local Asset (Khronos glTF Samples)",
        "poly_count": 14000,
        "file_size_mb": 3.7,
        "description": "A battle-damaged sci-fi helmet representing cranial and neural anatomy.",
    },
    {
        "id": "duck-005",
        "name": "Golden Duck",
        "tags": ["duck", "bird", "animal", "dna", "molecule", "genetics", "biology", "helix", "cellular", "genes", "rna", "organic"],
        "category": "biology",
        "url": "/models/duck.glb",
        "thumbnail": "",
        "source": "Local Asset (Khronos glTF Samples)",
        "poly_count": 4000,
        "file_size_mb": 0.12,
        "description": "A classic golden duck — used as a placeholder for molecular biology visualization.",
    },
    {
        "id": "flamingo-006",
        "name": "Flamingo",
        "tags": ["flamingo", "bird", "heart", "cardiac", "cardiovascular", "organ", "medical", "blood", "anatomy"],
        "category": "anatomy",
        "url": "/models/flamingo.glb",
        "thumbnail": "",
        "source": "Local Asset (Three.js Samples)",
        "poly_count": 3000,
        "file_size_mb": 0.07,
        "description": "An animated flamingo model used as an anatomy placeholder.",
    },
    {
        "id": "solar-007",
        "name": "Solar System / Space",
        "tags": ["solar", "system", "planets", "astronomy", "space", "sun", "earth", "orbit", "galaxy", "universe", "cosmic", "star"],
        "category": "astronomy",
        "url": "/models/astronaut.glb",
        "thumbnail": "",
        "source": "Local Asset (Placeholder - Space)",
        "poly_count": 15000,
        "file_size_mb": 2.7,
        "description": "Space exploration visualization using an astronaut model as a placeholder.",
    },
]


def retrieve_models(search_profile: dict, max_results: int = 5) -> list[dict]:
    """
    Search the model database using the expanded search profile.
    Returns a ranked list of candidate models.
    """
    candidates = []

    search_terms = (
        search_profile.get("search_keywords", [])
        + search_profile.get("semantic_alternatives", [])
        + [search_profile.get("core_entity", "").lower()]
    )

    for model in MODEL_DATABASE:
        score = 0
        model_text = " ".join(model["tags"] + [model["name"].lower(), model["description"].lower()])

        for term in search_terms:
            if term.lower() in model_text:
                score += 10

        # Category bonus
        if model.get("category") == search_profile.get("category"):
            score += 20

        if score > 0:
            candidates.append({
                **model,
                "relevance_score": score,
            })

    # Sort by relevance descending
    candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
    return candidates[:max_results]


async def search_sketchfab(query: str, api_key: Optional[str] = None) -> list[dict]:
    """
    Search the Sketchfab API for downloadable 3D models.
    This is a real API integration (requires API key).
    Falls back to local database if no key is provided.
    """
    if not api_key:
        return []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.sketchfab.com/v3/search",
                params={
                    "type": "models",
                    "q": query,
                    "downloadable": "true",
                    "sort_by": "-relevance",
                    "count": 5,
                },
                headers={"Authorization": f"Token {api_key}"},
            )
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("results", []):
                    results.append({
                        "id": item["uid"],
                        "name": item["name"],
                        "url": item.get("archives", {}).get("glb", {}).get("url", ""),
                        "thumbnail": item.get("thumbnails", {}).get("images", [{}])[0].get("url", ""),
                        "source": "Sketchfab",
                        "description": item.get("description", "")[:200],
                        "poly_count": item.get("faceCount", 0),
                    })
                return results
    except Exception:
        pass

    return []
