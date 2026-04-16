from fastapi import APIRouter, HTTPException, Depends
from app.models.queue_model import AIRequest
from app.utils.ai_assistant import get_doctor_suggestion
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])

@router.post("/suggest")
async def suggest_doctor(
    body: AIRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        result = await get_doctor_suggestion(body.symptoms)
        return {
            "success": True,
            "patient": current_user["name"],
            "symptoms": body.symptoms,
            "suggestion": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")