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

# --- Static Files ---
# Serve local models and cached generations from the backend
static_path = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_path):
    os.makedirs(os.path.join(static_path, "models"), exist_ok=True)
    os.makedirs(os.path.join(static_path, "generated"), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_path), name="static")

# --- Include Routers ---
app.include_router(router)


@app.get("/")
async def root():
    return {
        "service": "AI 3D Visualization System",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "search": "/api/search?q=<your_query>",
            "models": "/api/models",
            "health": "/api/health",
        },
    }
