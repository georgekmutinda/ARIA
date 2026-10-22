from fastapi import APIRouter

router = APIRouter(
    prefix ="/health",
    tags=["Health checks"],
)

@router.get("/")
async def health_check():
    return{
        "status":"ok",
        "service":"ARIA",
        "message":"API is healthy and running"
    }
    