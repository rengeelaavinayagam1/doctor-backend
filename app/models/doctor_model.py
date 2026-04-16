from pydantic import BaseModel
from typing import Optional, List

class ScheduleSlot(BaseModel):
    day: str
    start_time: str
    end_time: str
    slot_duration_minutes: int = 20
    max_patients: int = 20

class DoctorUpdateRequest(BaseModel):
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[int] = None
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None
    is_available: Optional[bool] = None
    schedule: Optional[List[ScheduleSlot]] = None
    hopital: Optional[str] = None
    timing: Optional[str] = None

class TimeSlot(BaseModel):
    start_time: str
    end_time: str
    is_booked: bool = False