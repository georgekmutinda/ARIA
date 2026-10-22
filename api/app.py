import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from api.routes.health import router as health_router
from api.routes.prediction import router as prediction_router
from services.inference import InferenceService
from api.routes.documents import router as documents_router
from services.storage import StorageService


BASE_DIR = Path(__file__).resolve().parents[1]

CHECKPOINT_PATH = (
    BASE_DIR
    / "checkpoints"
    / "simple_classifier.pth"
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup
    app.state.inference_service = InferenceService(
        checkpoint_path=CHECKPOINT_PATH
    )
    # FIX: Corrected "acess_key" to "access_key"
    app.state.storage_service = StorageService(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        bucket_name=os.getenv("MINIO_BUCKET_NAME", "aria"),
        secure=False,
    )

    yield

    # Shutdown
    app.state.inference_service = None


def create_app() -> FastAPI:

    app = FastAPI(
        title="ARIA",
        version="0.1.0",
        description="AI Research and Study Assistant",
        lifespan=lifespan,
    )

    app.include_router(health_router)
    app.include_router(prediction_router)
    # FIX: Changed app.include to app.include_router
    app.include_router(documents_router) 

    return app
