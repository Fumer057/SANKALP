"""
Query Processing & Semantic Expansion Service.

Takes a raw user query and expands it into a structured search profile
with core entity, structural components, and semantic alternatives.
"""
import re


def expand_query(raw_query: str) -> dict:
    """
    Process a raw user query and produce a structured search profile.

    In production, this would call an LLM (e.g., GPT-4o) to parse the query.
    For the prototype, we use keyword-based heuristics.
    """
    query_lower = raw_query.strip().lower()

    # --- Knowledge base of known concepts and their expansions ---
    knowledge_base = {
        "heart": {
            "core_entity": "Human Heart",
            "category": "anatomy",
            "structural_components": [
                "left ventricle", "right ventricle",
                "left atrium", "right atrium",
                "aorta", "pulmonary artery",
                "mitral valve", "tricuspid valve",
            ],
            "semantic_alternatives": [
                "cardiac organ", "cardiovascular anatomy",
                "heart anatomy", "cardiac muscle",
            ],
            "search_keywords": ["heart", "cardiac", "anatomical heart", "human heart model"],
        },
        "brain": {
            "core_entity": "Human Brain",
            "category": "anatomy",
            "structural_components": [
                "cerebrum", "cerebellum", "brainstem",
                "frontal lobe", "temporal lobe", "parietal lobe",
                "occipital lobe", "corpus callosum",
            ],
            "semantic_alternatives": [
                "cerebral anatomy", "neural organ", "encephalon",
            ],
            "search_keywords": ["brain", "cerebral", "human brain model", "neuroscience"],
        },
        "engine": {
            "core_entity": "Internal Combustion Engine",
            "category": "mechanical",
            "structural_components": [
                "cylinder", "piston", "crankshaft",
                "camshaft", "spark plug", "valve",
                "connecting rod", "flywheel",
            ],
            "semantic_alternatives": [
                "motor", "combustion engine", "car engine",
            ],
            "search_keywords": ["engine", "motor", "combustion engine", "mechanical engine"],
        },
        "dna": {
            "core_entity": "DNA Double Helix",
            "category": "biology",
            "structural_components": [
                "nucleotide", "base pair", "sugar-phosphate backbone",
                "adenine", "thymine", "guanine", "cytosine",
            ],
            "semantic_alternatives": [
                "deoxyribonucleic acid", "genetic material", "chromosome",
            ],
            "search_keywords": ["dna", "double helix", "molecule", "genetics"],
        },
        "solar": {
            "core_entity": "Solar System",
            "category": "astronomy",
            "structural_components": [
                "sun", "mercury", "venus", "earth", "mars",
                "jupiter", "saturn", "uranus", "neptune",
            ],
            "semantic_alternatives": [
                "planetary system", "heliocentric model", "planets",
            ],
            "search_keywords": ["solar system", "planets", "astronomy", "space"],
        },
        "cell": {
            "core_entity": "Animal Cell",
            "category": "biology",
            "structural_components": [
                "nucleus", "mitochondria", "endoplasmic reticulum",
                "golgi apparatus", "cell membrane", "ribosome",
            ],
            "semantic_alternatives": [
                "eukaryotic cell", "cellular biology", "cell anatomy",
            ],
            "search_keywords": ["cell", "animal cell", "biology", "cellular"],
        },
    }

    # --- Match query to the knowledge base ---
    best_match = None
    best_score = 0

    for key, profile in knowledge_base.items():
        score = 0
        # Check if the key appears in the query
        if key in query_lower:
            score += 10
        # Check search keywords
        for kw in profile["search_keywords"]:
            if kw in query_lower:
                score += 5
        # Check semantic alternatives
        for alt in profile["semantic_alternatives"]:
            if alt in query_lower:
                score += 3

        if score > best_score:
            best_score = score
            best_match = key

    if best_match and best_score > 0:
        profile = knowledge_base[best_match]
        return {
            "original_query": raw_query,
            "core_entity": profile["core_entity"],
            "category": profile["category"],
            "structural_components": profile["structural_components"],
            "semantic_alternatives": profile["semantic_alternatives"],
            "search_keywords": profile["search_keywords"],
            "match_confidence": min(best_score * 10, 100),
        }

    # --- Fallback: generic expansion ---
    words = re.findall(r'\w+', query_lower)
    return {
        "original_query": raw_query,
        "core_entity": raw_query.strip().title(),
        "category": "general",
        "structural_components": [],
        "semantic_alternatives": words,
        "search_keywords": words + [query_lower],
        "match_confidence": 30,
    }
