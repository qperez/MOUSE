from flask import Blueprint, request, abort, jsonify

from mouse_server_serial_hub.mouse.shared.shared_haptic_service import SharedHapticService

vibration_bp = Blueprint('vibration', __name__)

shared_haptic_service = SharedHapticService()


@vibration_bp.route("/on")
def on():
    vibration_duration = request.args.get("duration",type=int)
    pwm_value = request.args.get("pwm",type=int)
    if not 0 <= pwm_value <= 255:
        abort(400, "Invalid pwm value") 
    shared_haptic_service.vibration_to_serial(vibration_duration, pwm_value)

    return jsonify(status="ok", action="vibration on", duration=vibration_duration, pwm=pwm_value)

@vibration_bp.route("/loop")
def loop():
    vibration_duration = request.args.get("vibration-duration",type=int)
    pwm_value = request.args.get("pwm",type=int)
    if not 0 <= pwm_value <= 255:
        abort(400, "Invalid pwm value") 
    nb_repetitions = request.args.get("nb-repetitions",type=int)
    time_between_vibration = request.args.get("time-between-vibration",type=int)

    shared_haptic_service.vibration_to_serial(vibration_duration, pwm_value, nb_repetitions, time_between_vibration)

    return jsonify(status="ok",
                   action="vibration on",
                   vibration_duration=int(vibration_duration),
                   pwm=int(pwm_value),
                   nb_repetitions=int(nb_repetitions),
                   time_between_vibration=int(time_between_vibration))

