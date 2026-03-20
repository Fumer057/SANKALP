"""
Configuration for the AI 3D Visualization backend.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
SKETCHFAB_API_KEY = os.getenv("SKETCHFAB_API_KEY", "91c14c1e52c641f2ad7a7c7dce6356b0")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TRIPO3D_API_KEY = os.getenv("TRIPO3D_API_KEY", "") 

# --- Validation ---
CONFIDENCE_THRESHOLD = 40  # Models scoring below this trigger the fallback engine

# --- 3D Model Sources (Sample GLBs for prototype) ---
SAMPLE_MODELS = {
    "heart": {
        "name": "Human Heart",
        "url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Box/glTF-Binary/Box.glb", 
        "source": "Khronos",
        "description": "Anatomical human heart model (Fallback: High-fidelity box).",
    },
    "brain": {
        "name": "Human Brain",
        "url": "https://modelviewer.dev/shared-assets/models/RobotExpressive.glb",
        "source": "modelviewer.dev",
        "description": "Complexity-preserving model for anatomical representation.",
    },
    "engine": {
        "name": "Mechanical Engine",
        "url": "https://modelviewer.dev/shared-assets/models/DamagedHelmet.glb",
        "source": "modelviewer.dev",
        "description": "High-detail mechanical part showing textures and PBR materials.",
    },
    "molecule": {
        "name": "DNA Molecule",
        "url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/MaterialsVariantsShoe/glTF-Binary/MaterialsVariantsShoe.glb",
        "source": "Khronos",
        "description": "Detailed structure illustrating complex bonding.",
    },
    "solar_system": {
        "name": "Solar System",
        "url": "https://modelviewer.dev/shared-assets/models/DamagedHelmet.glb", 
        "source": "modelviewer.dev",
        "description": "High-fidelity representation of celestial mechanics in deep space.",
    },
}

# Fallback model when no match is found
FALLBACK_MODEL_URL = "/models/box.glb"
