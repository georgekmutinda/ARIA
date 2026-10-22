from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from api.dependencies import get_inference_service
from api.schemas.prediction import PredictionResponse
from services.inference import InferenceService


router = APIRouter(
    prefix="/predict",
    tags=["Prediction"],
)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post(
    "",
    response_model=PredictionResponse,
)
async def predict(
    file: UploadFile = File(...),
    inference_service: InferenceService = Depends(
        get_inference_service
    ),
) -> PredictionResponse:

    # -------------------------
    # 1. Validate content type
    # -------------------------

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type.",
        )

    # -------------------------
    # 2. Validate file size
    # -------------------------

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image exceeds the 5 MB size limit.",
        )

    # -------------------------
    # 3. Validate actual image
    # -------------------------

    try:
        contents = await file.read()

        image = Image.open(BytesIO(contents))
        image.verify()

        image = Image.open(BytesIO(contents))
        image.load()

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid image.",
        )

    # -------------------------
    # 4. Send to AI service
    # -------------------------

    class_name, confidence = inference_service.predict(image)

    # -------------------------
    # 5. Return API contract
    # -------------------------

    return PredictionResponse(
        class_name=class_name,
        confidence=confidence,
    )