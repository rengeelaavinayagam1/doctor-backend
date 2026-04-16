from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime

from app.config.database import get_db
from app.models.user_model import RegisterPatientRequest, RegisterDoctorRequest, LoginRequest
from app.utils.password_utils import hash_password, verify_password
from app.utils.jwt_utils import create_access_token
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register")
async def register_patient(body: RegisterPatientRequest):
    db = get_db()
    if await db["users"].find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = {
        "name": body.name,
        "email": body.email,
        "password": hash_password(body.password),
        "phone": body.phone,
        "role": "patient",
        "is_active": True,
        "created_at": datetime.utcnow(),
    }
    result = await db["users"].insert_one(user)
    uid = str(result.inserted_id)
    return {"success": True, "token": create_access_token(uid), "user": {"id": uid, "name": body.name, "role": "patient"}}

@router.post("/register-doctor")
async def register_doctor(body: RegisterDoctorRequest):
    db = get_db()
    if await db["users"].find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = {
        "name": body.name, "email": body.email,
        "password": hash_password(body.password),
        "phone": body.phone, "role": "doctor",
        "is_active": True, "created_at": datetime.utcnow(),
    }
    user_result = await db["users"].insert_one(user)
    uid = str(user_result.inserted_id)
    doctor = {
        "user_id": uid, "specialization": body.specialization,
        "qualification": body.qualification, "experience": body.experience,
        "hospital": {"name": body.hospital_name, "address": body.hospital_address, "city": body.city, "state": body.state},
        "schedule": [], "rating": 0.0, "total_ratings": 0,
        "is_available": True, "created_at": datetime.utcnow(),
    }
    doc_result = await db["doctors"].insert_one(doctor)
    return {"success": True, "token": create_access_token(uid), "doctor_id": str(doc_result.inserted_id)}

@router.post("/login")
async def login(body: LoginRequest):
    db = get_db()
    user = await db["users"].find_one({"email": body.email})
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    uid = str(user["_id"])
    return {"success": True, "token": create_access_token(uid), "user": {"id": uid, "name": user["name"], "role": user["role"]}}

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"success": True, "user": {"id": current_user["id"], "name": current_user["name"], "role": current_user["role"]}}