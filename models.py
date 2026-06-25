import threading
from datetime import datetime, timezone

monitors = {}

def create_monitor(device_id, timeout_seconds, alert_email):
    monitors[device_id] = {
        "id": device_id,
        "timeout_seconds": timeout_seconds,
        "alert_email": alert_email,
        "missed_count": 0,
        "status": "active",
        "last_heartbeat": datetime.now(timezone.utc)
    }

    return monitors[device_id]

monitor_lock = threading.Lock()