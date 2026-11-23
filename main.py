from fastapi import FastAPI

from app.routes.profiling import router as profiling_router
from app.routes.quality import router as quality_router
from app.routes.orchestration import router as orchestration_router
from app.routes.datasets import router as datasets_router
from app.routes.semantic import router as semantic_router
from app.routes.preprocessing import router as preprocessing_router

app = FastAPI(
    title="Team 2 Profiling, Data Quality, Semantic and Preprocessing API",
    description="Team 2 Backend integration for Profiling, Data Quality, Orchestration, Datasets and Semantic Understanding",
    version="1.0"
)

app.include_router(profiling_router)
app.include_router(quality_router)
app.include_router(orchestration_router)
app.include_router(datasets_router)
app.include_router(semantic_router)
app.include_router(preprocessing_router)


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
