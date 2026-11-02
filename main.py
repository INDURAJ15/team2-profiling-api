from fastapi import FastAPI
from app.routes.profiling import router as profiling_router
from app.routes.quality import router as quality_router

app = FastAPI(
    title="Team 2 Profiling and Data Quality API",
    description="Backend integration for Profiling and Data Quality services",
    version="1.0"
)

app.include_router(profiling_router)
app.include_router(quality_router)


@app.get("/")
def home():
    return {
        "message": "Team 2 Backend API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }