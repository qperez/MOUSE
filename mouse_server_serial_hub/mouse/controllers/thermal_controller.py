from flask import Blueprint, request, abort, jsonify

from mouse_server_serial_hub.mouse.shared.shared_haptic_service import SharedHapticService

thermal_bp = Blueprint('thermal', __name__)

shared_haptic_service = SharedHapticService()

@thermal_bp.route("/on")
def thermal_poweron():
    heating_duration = request.args.get("duration", type=int)
    pwm_value = request.args.get("pwm", type=int)
    if heating_duration is None:
        abort(400, description="duration must be an integer")
    if pwm_value is None or not 0 <= pwm_value <= 255:
        abort(400, description="pwm must be an integer between 0 and 255")

    shared_haptic_service.thermal_to_serial(heating_duration, pwm_value)

    return jsonify(status="ok", action="heat", duration=heating_duration, pwm=pwm_value)
