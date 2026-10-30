from datetime import datetime, timezone

from app.database import activity_logs


def log_activity(user_id, action, details=None):
    """Save one activity (like 'post' or 'follow') to MongoDB."""
    if details is None:
        details = {}
    activity_logs.insert_one({
        "user_id": user_id,
        "action": action,
        "details": details,
        "created_at": datetime.now(timezone.utc),
    })


def get_user_activity(user_id, limit=20):
    """Return the newest activities of a user."""
    # {"_id": 0} leaves out MongoDB's own id field
    cursor = activity_logs.find({"user_id": user_id}, {"_id": 0})
    cursor = cursor.sort("created_at", -1).limit(limit)
    return list(cursor)
