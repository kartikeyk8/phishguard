from fastapi import APIRouter, Depends
from backend.services.analytics_service import get_user_analytics
from backend.utils.dependencies import get_current_user

router = APIRouter()

@router.get("/me")
def my_analytics(current_user=Depends(get_current_user)):
    return get_user_analytics(current_user["id"])
