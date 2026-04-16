from datetime import datetime
from app.config.database import get_db

async def send_notification(user_id: str, notif_type: str, title: str, message: str, metadata: dict = {}):
    try:
        db = get_db()
        await db["notifications"].insert_one({
            "user_id": user_id,
            "type": notif_type,
            "title": title,
            "message": message,
            "is_read": False,
            "metadata": metadata,
            "created_at": datetime.utcnow(),
        })
    except Exception as e:
        print(f"Notification error: {e}")