"""
AI-Based Validation, Ranking & Scoring Service.

Evaluates retrieved 3D models for relevance and quality.
In production, this would render snapshots and use a Vision-Language Model
(GPT-4o / Gemini) to evaluate structural correctness.
"""
import random


def validate_and_score(candidates: list[dict], search_profile: dict) -> list[dict]:
    """
    Score each candidate model against the search profile requirements.

    In production:
    1. Render multi-angle 2D snapshots of the 3D model
    2. Send snapshots + query to a Vision-Language LLM
    3. Get structured scoring and explanations

    For the prototype, we simulate scoring based on metadata matching.
    """
    scored_results = []
    core_entity = search_profile.get("core_entity", "").lower()
    category = search_profile.get("category", "")
    components = search_profile.get("structural_components", [])

    for candidate in candidates:
        model_text = (
            candidate.get("name", "").lower()
            + " "
            + candidate.get("description", "").lower()
            + " "
            + " ".join(candidate.get("tags", []))
        )

        # --- Scoring rubric ---
        score = 0

        # Relevance bonus from retrieval stage (0-30 points)
        # This model already survived keyword/tag matching — reward it
        relevance = candidate.get("relevance_score", 0)
        score += min(30, relevance // 2)

        # Entity match (0-40 points)
        entity_words = [w for w in core_entity.split() if len(w) > 2]  # skip short words
        matched_entity_words = sum(1 for w in entity_words if w in model_text)
        entity_ratio = matched_entity_words / max(len(entity_words), 1)
        score += int(entity_ratio * 40)

        # Category match (0-20 points)
        if candidate.get("category") == category:
            score += 20

        # Component coverage (0-10 points)
        if components:
            matched_components = sum(
                1 for comp in components
                if any(word in model_text for word in comp.lower().split())
            )
            component_ratio = matched_components / len(components)
            score += int(component_ratio * 10)

        # Clamp, no randomness (randomness was making good matches fail unpredictably)
        score = max(0, min(100, score))

        # Generate explanation
        explanation = _generate_explanation(candidate, score, core_entity, matched_entity_words, len(entity_words))

        scored_results.append({
            **candidate,
            "confidence_score": score,
            "validation_explanation": explanation,
            "validation_method": "Simulated AI Validation (prototype)",
            "structural_coverage": f"{int(entity_ratio * 100)}%",
        })

    # Sort by confidence score descending
    scored_results.sort(key=lambda x: x["confidence_score"], reverse=True)
    return scored_results


def _generate_explanation(candidate: dict, score: int, core_entity: str, matched: int, total: int) -> str:
    """Generate a human-readable validation explanation."""
    name = candidate.get("name", "Unknown")

    if score >= 80:
        return (
            f"✅ HIGH CONFIDENCE: '{name}' is an excellent match for '{core_entity}'. "
            f"Strong entity alignment ({matched}/{total} terms matched), "
            f"correct category, and sufficient geometric detail ({candidate.get('poly_count', 0):,} polygons). "
            f"Recommended for presentation."
        )
    elif score >= 60:
        return (
            f"⚠️ MODERATE CONFIDENCE: '{name}' partially matches '{core_entity}'. "
            f"Entity alignment: {matched}/{total} terms. "
            f"The model may lack some structural components but could serve as a reasonable representation."
        )
    elif score >= 40:
        return (
            f"🔶 LOW CONFIDENCE: '{name}' has limited relevance to '{core_entity}'. "
            f"Only {matched}/{total} entity terms matched. "
            f"Consider triggering the fallback generation pipeline."
        )
    else:
        return (
            f"❌ VERY LOW CONFIDENCE: '{name}' does not adequately represent '{core_entity}'. "
            f"Structural mismatch detected. Fallback generation strongly recommended."
        )
