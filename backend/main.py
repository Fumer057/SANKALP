"""
AI 3D Visualization System - Backend Server
"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from routes import router

app = FastAPI(
    title="AI 3D Visualization System",
    version="0.1.0",
)

# --- CORS Middleware (Global) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# --- Hardened Static Files with Mandatory CORS Headers ---
class CORSStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")
models_path = os.path.join(static_path, "models")
gen_path = os.path.join(static_path, "generated")

# Ensure directories exist
os.makedirs(static_path, exist_ok=True)
os.makedirs(models_path, exist_ok=True)
os.makedirs(gen_path, exist_ok=True)

# Mount the custom CORS-enabled static file server
app.mount("/static", CORSStaticFiles(directory=static_path), name="static")

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Warm up AI clients on boot."""
    print("\n--- AI SYSTEM WARMING UP ---")
    try:
        from services.fallback import get_shape_client
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, get_shape_client)
        print("Shap-E primed for high-reliability presentation.\n")
    except Exception as e:
        print(f"Warm-up status: {e}")

@app.get("/")
async def root():
    return {"service": "SANKALP AI", "status": "online"}
