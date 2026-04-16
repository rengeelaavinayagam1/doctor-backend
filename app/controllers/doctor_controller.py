from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId
from typing import Optional
from app.config.database import get_db
from app.middleware.auth_middleware import get_current_user, require_role

router = APIRouter(prefix="/api/doctors", tags=["Doctors"])

@router.get("/")
async def search_doctors(
    specialization: Optional[str] = None,
    city: Optional[str] = None,
    name: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
):
    db = get_db()
    query = {"is_available": True}
    if specialization:
        query["specialization"] = {"$regex": specialization, "$options": "i"}
    if city:
        query["hospital.city"] = {"$regex": city, "$options": "i"}

    cursor = db["doctors"].find(query).skip((page-1)*limit).limit(limit)
    docs = await cursor.to_list(length=limit)
    results = []
    for doc in docs:
        user = await db["users"].find_one({"_id": ObjectId(doc["user_id"])})
        d = {
            "id": str(doc["_id"]),
            "name": user.get("name", "") if user else "",
            "specialization": doc.get("specialization", ""),
            "hospital": doc.get("hospital", {}),
            "schedule": doc.get("schedule",{}),
            "rating": doc.get("rating", 0),
            "consultation_fee": doc.get("consultation_fee", 0),
            "is_available": doc.get("is_available", True),
        }
        if name and name.lower() not in d["name"].lower():
            continue
        results.append(d)
    return {"success": True, "count": len(results), "doctors": results}

@router.get("/{doctor_id}")
async def get_doctor(doctor_id: str):
    db = get_db()
    doc = await db["doctors"].find_one({"_id": ObjectId(doctor_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    user = await db["users"].find_one({"_id": ObjectId(doc["user_id"])})
    return {
        "success": True,
        "doctor": {
            "id": str(doc["_id"]),
            "name": user.get("name", "") if user else "",
            "specialization": doc.get("specialization", ""),
            "qualification": doc.get("qualification", ""),
            "experience": doc.get("experience", 0),
            "hospital": doc.get("hospital", {}),
            "schedule": doc.get("schedule", []),
            "rating": doc.get("rating", 0),
            "consultation_fee": doc.get("consultation_fee", 0),
            "is_available": doc.get("is_available", True),
        }
    }