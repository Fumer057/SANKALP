"""
AI 3D Visualization System - Backend Server

A FastAPI backend that orchestrates the intelligent 3D model retrieval,
validation, and fallback generation pipeline.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
