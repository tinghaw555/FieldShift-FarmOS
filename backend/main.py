"""
FieldShift FarmOS - FastAPI Backend
NASA Space Apps Challenge 2026
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add services to path
sys.path.append(str(Path(__file__).parent))

from database.db import init_database
from routers import farms, climate, rotations, weather, simulator, ground_truth, hardware, planting, farm_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    await init_database()
    yield

app = FastAPI(
    title="FieldShift FarmOS API",
    description="Agricultural decision-support system using NASA Earth observations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(farms.router, prefix="/api/farms", tags=["Farms"])
app.include_router(climate.router, prefix="/api/climate", tags=["Climate"])
app.include_router(rotations.router, prefix="/api/rotations", tags=["Rotations"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(simulator.router, prefix="/api/simulator", tags=["Simulator"])
app.include_router(hardware.router, prefix="/api/hardware", tags=["Hardware"])
app.include_router(ground_truth.router, prefix="/api/ground-truth", tags=["Ground Truth"])
app.include_router(planting.router, prefix="/api", tags=["Planting Suitability"])
app.include_router(farm_data.router, tags=["Farm Data"])

@app.get("/")
async def root():
    """API health check"""
    return {
        "name": "FieldShift FarmOS API",
        "version": "1.0.0",
        "status": "operational",
        "tagline": "Observe Earth. Predict Risks. Improve Decisions. Verify Reality."
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "operational",
        "nasa_power": "available",
        "open_meteo": "available"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
