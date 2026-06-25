from models import  monitor_lock, monitors
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()

def schedule_expiry(device_id, timeout_seconds):
    expiry_time = datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)
    scheduler.add_job(id=device_id, func=expire_monitor, trigger='date', run_date=expiry_time, args=[device_id], replace_existing=True)

def cancel_expiry(device_id):
    job = scheduler.get_job(device_id)
    if job:
        scheduler.remove_job(device_id)


def expire_monitor(device_id):
    with monitor_lock:
        if device_id not in monitors or monitors[device_id]["status"] != "active":
            return 
        if monitors[device_id]['missed_count'] == 0:
            monitors[device_id]['missed_count'] += 1
            schedule_expiry(device_id, monitors[device_id]['timeout_seconds'])
            print("first grace period heartbeat missed for device_id {}. Missed count: {}".format(device_id, monitors[device_id]['missed_count']))
        else:
            monitors[device_id]['status'] = "down"
            print("ALERT: Monitor for device_id {} has expired. Sending alert to {}".format(device_id, monitors[device_id]['alert_email']))