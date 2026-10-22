from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from api.dependencies import get_document_service
from api.schemas.document import DocumentAcceptedResponse
from services.document_service import DocumentService

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.post(
    "",
    response_model=DocumentAcceptedResponse,
    status_code = status.HTTP_202_ACCEPTED
    
)
async def upload_documnet(
    file: UploadFile=File(...),
    service: DocumentService = Depends(get_document_service),
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="filename is required")
    
    if file.content_type not in {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "text/plain",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported  document type.",
        )
        
    file.file.seek(0,2)
    size_bytes=file.file.tell()
    file.file.seek(0)
    
    if size_bytes> 50*1024*1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Document exceeds the 50 MB size limit.",
        )
        
    document =  service.create_document(
        file = file,
        size_bytes = size_bytes,
    )
    
    return DocumentAcceptedResponse(
        document_id=document.id,
        filename=document.filename,
        status=document.status, 
    )