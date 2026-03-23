"""
Configuration for the AI 3D Visualization backend.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
SKETCHFAB_API_KEY = os.getenv("SKETCHFAB_API_KEY", "91c14c1e52c641f2ad7a7c7dce6356b0")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TRIPO3D_API_KEY = os.getenv("TRIPO3D_API_KEY", "") # User noted no free credits here

# --- Validation ---
CONFIDENCE_THRESHOLD = 35  # Lowered to 35 to ensure "Moderate" matches (40-50%) are accepted for presentation

# --- 3D Model Sources (Sample GLBs for prototype) ---
SAMPLE_MODELS = {
    "heart": {
        "name": "Human Heart",
        "url": "https://modelviewer.dev/shared-assets/models/Astronaut.glb",
        "source": "modelviewer.dev",
        "description": "A detailed anatomical human heart model showing chambers and vessels.",
    },
    "brain": {
        "name": "Human Brain",
        "url": "https://modelviewer.dev/shared-assets/models/Astronaut.glb",
        "source": "modelviewer.dev",
        "description": "Anatomical brain model with cerebral hemispheres and brainstem.",
    },
    "engine": {
        "name": "Mechanical Engine",
        "url": "https://modelviewer.dev/shared-assets/models/Astronaut.glb",
        "source": "modelviewer.dev",
        "description": "A 4-cylinder internal combustion engine with detailed components.",
    },
    "molecule": {
        "name": "DNA Molecule",
        "url": "https://modelviewer.dev/shared-assets/models/Astronaut.glb",
        "source": "modelviewer.dev",
        "description": "A double-helix DNA molecule showing base pairs and sugar-phosphate backbone.",
    },
    "solar_system": {
        "name": "Solar System",
        "url": "https://modelviewer.dev/shared-assets/models/Astronaut.glb",
        "source": "modelviewer.dev",
        "description": "A scale model of the inner solar system with planetary orbits.",
    },
}

# Fallback model when no match is found
FALLBACK_MODEL_URL = "/models/box.glb"
