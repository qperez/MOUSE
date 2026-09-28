from flask import Blueprint, request, abort, jsonify

from mouse_server_serial_hub.mouse.shared.shared_haptic_service import SharedHapticService

vibration_bp = Blueprint('vibration', __name__)

shared_haptic_service = SharedHapticService()


@vibration_bp.route("/on")
def on():
    vibration_duration = int(request.args.get("duration"))
    pwm_value = int(request.args.get("pwm"))

    shared_haptic_service.vibration_to_serial(vibration_duration, pwm_value)

    return jsonify(status="ok", action="vibration on", duration=vibration_duration, pwm=pwm_value)

@vibration_bp.route("/loop")
def loop():
    vibration_duration = int(request.args.get("vibration-duration"))
    pwm_value = int(request.args.get("pwm"))
    nb_repetitions = int(request.args.get("nb-repetitions"))
    time_between_vibration = int(request.args.get("time-between-vibration"))

    shared_haptic_service.vibration_to_serial(vibration_duration, pwm_value, nb_repetitions, time_between_vibration)

    return jsonify(status="ok",
                   action="vibration on",
                   vibration_duration=int(vibration_duration),
                   pwm=int(pwm_value),
                   nb_repetitions=int(nb_repetitions),
                   time_between_vibration=int(time_between_vibration))

