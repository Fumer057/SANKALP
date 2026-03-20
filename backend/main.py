"""
AI 3D Visualization System - Backend Server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from routes import router

app = FastAPI(
    title="AI 3D Visualization System",
    version="0.1.0",
)

# --- CORS Middleware (Comprehensive) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Files (Forced Path Creation) ---
# Ensure absolute paths for stability on Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")
models_path = os.path.join(static_path, "models")
gen_path = os.path.join(static_path, "generated")

# Always ensure these exist on startup
os.makedirs(static_path, exist_ok=True)
os.makedirs(models_path, exist_ok=True)
os.makedirs(gen_path, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_path), name="static")
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Warm up Shap-E client on boot."""
    print("\n--- AI SYSTEM WARMING UP ---")
    try:
        from services.fallback import get_shape_client
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, get_shape_client)
        print("Shap-E connection initiated... safe for presentation.\n")
    except Exception as e:
        print(f"Warm-up failed (non-critical): {e}")

@app.get("/")
async def root():
    return {"service": "SANKALP AI", "status": "online"}
