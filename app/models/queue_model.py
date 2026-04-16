from pydantic import BaseModel
from typing import Optional

class CheckInRequest(BaseModel):
    doctor_id: str
    date: str

class QueueStatusResponse(BaseModel):
    success: bool
    checked_in: bool
    token_number: Optional[str] = None
    your_position: Optional[int] = None
    current_token: Optional[int] = None
    ahead_of_you: Optional[int] = None
    estimated_wait_minutes: Optional[int] = None
    status: Optional[str] = None
    message: Optional[str] = None

class AIRequest(BaseModel):
    symptoms: str