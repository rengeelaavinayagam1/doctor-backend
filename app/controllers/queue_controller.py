from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
from app.config.database import get_db
from app.models.queue_model import CheckInRequest
from app.middleware.auth_middleware import get_current_user, require_role
from app.utils.notification_utils import send_notification

router = APIRouter(prefix="/api/queue", tags=["Queue"])

class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        self.rooms.setdefault(room, []).append(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.rooms:
            self.rooms[room].remove(websocket)

    async def broadcast(self, room: str, data: dict):
        for ws in self.rooms.get(room, []):
            try:
                await ws.send_json(data)
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/ws/{doctor_id}/{date}")
async def queue_websocket(websocket: WebSocket, doctor_id: str, date: str):
    room = f"queue_{doctor_id}_{date}"
    await manager.connect(websocket, room)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)

@router.post("/check-in")
async def check_in(body: CheckInRequest, current_user: dict = Depends(get_current_user)):
    db = get_db()
    queue = await db["queues"].find_one({"doctor_id": body.doctor_id, "date": body.date})
    if not queue:
        queue_doc = {"doctor_id": body.doctor_id, "date": body.date, "current_token": 0, "entries": []}
        result = await db["queues"].insert_one(queue_doc)
        queue = await db["queues"].find_one({"_id": result.inserted_id})

    waiting = [e for e in queue.get("entries", []) if e["status"] == "waiting"]
    position = len(waiting) + 1
    token = f"T-{position:03d}"

    entry = {
        "patient_id": current_user["id"],
        "patient_name": current_user["name"],
        "token_number": token,
        "position": position,
        "status": "waiting",
        "checked_in_at": datetime.utcnow().isoformat(),
    }
    await db["queues"].update_one({"_id": queue["_id"]}, {"$push": {"entries": entry}})
    await manager.broadcast(f"queue_{body.doctor_id}_{body.date}", {"type": "check_in", "token": token, "position": position})
    return {"success": True, "token_number": token, "position": position, "estimated_wait_minutes": (position-1)*10}

@router.get("/status/{doctor_id}/{date}")
async def get_status(doctor_id: str, date: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    queue = await db["queues"].find_one({"doctor_id": doctor_id, "date": date})
    if not queue:
        return {"success": True, "checked_in": False, "message": "Queue not started"}
    entry = next((e for e in queue["entries"] if e["patient_id"] == current_user["id"]), None)
    if not entry:
        return {"success": True, "checked_in": False, "message": "Not checked in"}
    ahead = len([e for e in queue["entries"] if e["status"] == "waiting" and e["position"] < entry["position"]])
    return {"success": True, "checked_in": True, "token_number": entry["token_number"], "position": entry["position"], "ahead_of_you": ahead, "estimated_wait_minutes": ahead*10}

@router.put("/call-next")
async def call_next(current_user: dict = Depends(require_role("doctor"))):
    db = get_db()
    doctor = await db["doctors"].find_one({"user_id": current_user["id"]})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    queue = await db["queues"].find_one({"doctor_id": str(doctor["_id"]), "date": date_str})
    if not queue:
        raise HTTPException(status_code=404, detail="No queue today")
    entries = queue["entries"]
    for e in entries:
        if e["status"] == "in-consultation":
            e["status"] = "completed"
    next_entry = next((e for e in entries if e["status"] == "waiting"), None)
    if not next_entry:
        await db["queues"].update_one({"_id": queue["_id"]}, {"$set": {"entries": entries}})
        return {"success": True, "message": "No more patients"}
    next_entry["status"] = "in-consultation"
    await db["queues"].update_one({"_id": queue["_id"]}, {"$set": {"entries": entries, "current_token": next_entry["position"]}})
    await send_notification(next_entry["patient_id"], "your_turn", "உங்கள் முறை வந்தது! 🔔", f"Token {next_entry['token_number']} — Doctor room-க்கு வாருங்கள்!")
    await manager.broadcast(f"queue_{str(doctor['_id'])}_{date_str}", {"type": "next_called", "token": next_entry["token_number"]})
    return {"success": True, "called": next_entry["token_number"]}