"""
AI 3D Visualization System - Backend Server

A FastAPI backend that orchestrates the intelligent 3D model retrieval,
validation, and fallback generation pipeline.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from routes import router

app = FastAPI(
    title="AI 3D Visualization System",
    description=(
        "An intelligent system that retrieves, validates, and presents "
        "3D visual representations of concepts using AI-powered pipelines."
    ),
    version="0.1.0",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Files ---
static_path = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_path):
    os.makedirs(os.path.join(static_path, "models"), exist_ok=True)
    os.makedirs(os.path.join(static_path, "generated"), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_path), name="static")

# --- Include Routers ---
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Warm up AI clients in the background on boot."""
    print("\n--- AI SYSTEM WARMING UP ---")
    try:
        from services.fallback import get_tripo_client, get_shape_client, TRIPO_SPACES
        import asyncio
        
        loop = asyncio.get_event_loop()
        # Warm up the primary mirror
        loop.run_in_executor(None, lambda: get_tripo_client(TRIPO_SPACES[0]))
        # Warm up Shap-E
        loop.run_in_executor(None, get_shape_client)
        print("AI connections initiated... priming system for high speed.\n")
    except Exception as e:
        print(f"Warm-up failed: {e}")

@app.get("/")
async def root():
    return {
        "service": "AI 3D Visualization System",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "search": "/api/search?q=<your_query>",
            "models": "/api/gallery",
            "health": "/",
        },
    }
