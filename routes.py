from flask import Blueprint, jsonify, request
from scheduler import schedule_expiry,scheduler,cancel_expiry
from models import monitors, monitor_lock, create_monitor
from datetime import datetime, timezone

routes = Blueprint('monitors', __name__)

@routes.route('/monitors', methods=['POST'])
def create_monitor_route():
    data = request.get_json()
    device_id = data.get('id')
    timeout_seconds = data.get('timeout')
    alert_email = data.get('alert_email')

    if not device_id or not timeout_seconds or not alert_email:
        return jsonify({"error": "Missing required fields"}), 400


    if device_id in monitors:
        return jsonify({"error": "Monitor already exists for this device_id"}), 400
    monitor = create_monitor(device_id, timeout_seconds, alert_email)
    schedule_expiry(device_id, timeout_seconds)

    return jsonify(monitor), 201


@routes.route('/monitors/<device_id>/heartbeat', methods=['POST'])
def heartbeat(device_id):
    with monitor_lock:
        if device_id not in monitors:
            return jsonify({"error": "Monitor not found"}), 404

        monitor = monitors[device_id]

        monitor["last_heartbeat"] = datetime.now(timezone.utc)
        monitor["status"] = "active"
        monitor["missed_count"] = 0
        schedule_expiry(device_id, monitor["timeout_seconds"])
        print("Heartbeat received for device_id {}. Resetting expiry timer.".format(device_id))

    return jsonify({"message": "Heartbeat received"}), 200


@routes.route('/monitors/<device_id>/pause', methods=['POST'])
def pause_monitor(device_id):
    with monitor_lock:
        if device_id not in monitors:
            return jsonify({"error": "Monitor not found"}), 404

        monitor = monitors[device_id]
        monitor["status"] = "paused"
        cancel_expiry(device_id)
        print(f"Monitor for device_id {device_id} has been paused. Expiry timer canceled... Call heartbeat to resume monitoring.")

    return jsonify({"message": "Monitor paused"}), 200