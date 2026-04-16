from fastapi import APIRouter, Depends
from bson import ObjectId
from app.config.database import get_db
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("/")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db["notifications"].find(
        {"user_id": current_user["id"]}
    ).sort("created_at", -1).limit(20)
    notifs = await cursor.to_list(length=20)
    unread = await db["notifications"].count_documents(
        {"user_id": current_user["id"], "is_read": False}
    )
    for n in notifs:
        n["id"] = str(n["_id"])
        del n["_id"]
    return {"success": True, "unread_count": unread, "notifications": notifs}

@router.put("/{notif_id}/read")
async def mark_read(notif_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    await db["notifications"].update_one(
        {"_id": ObjectId(notif_id), "user_id": current_user["id"]},
        {"$set": {"is_read": True}}
    )
    return {"success": True, "message": "Marked as read"}

@router.put("/read-all")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    db = get_db()
    await db["notifications"].update_many(
        {"user_id": current_user["id"], "is_read": False},
        {"$set": {"is_read": True}}
    )
    return {"success": True, "message": "All marked as read"}