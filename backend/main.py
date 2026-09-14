# backend/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import settings
from api.routes import router as api_router

def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Banana Hacks 2026 - Image AI Upcycling Web Application",
        version="2.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Configure CORS origins for secure frontend-backend communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API Endpoints under /api/v1
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Automatically resolve and mount the frontend directory
    # This serves index.html, CSS, and JS directly from http://localhost:8000
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
    if os.path.exists(frontend_dir):
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    else:
        print(f"⚠️ Warning: Frontend directory not found at {frontend_dir}")

    return app

app = get_application()

if __name__ == "__main__":
    import uvicorn
    # Start the local development server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)