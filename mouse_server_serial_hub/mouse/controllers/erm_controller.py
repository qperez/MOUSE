from flask import Blueprint, request, abort, jsonify

from mouse_server_serial_hub.mouse.shared.shared_haptic_service import SharedHapticService

vibration_bp = Blueprint('vibration', __name__)

shared_haptic_service = SharedHapticService()


@vibration_bp.route("/on")
def on():
    vibration_duration = request.args.get("duration",type=int)
    pwm_value = request.args.get("pwm",type=int)
    if vibration_duration is None:
        abort(400, "duration must be an integer")
    if pwm_value is None or not 0 <= pwm_value <= 255:
        abort(400, "pwm must be an integer between 0 and 255")
    shared_haptic_service.vibration_to_serial(vibration_duration, pwm_value)

    return jsonify(status="ok", action="vibration on", duration=vibration_duration, pwm=pwm_value)

@vibration_bp.route("/loop")
def loop():
    vibration_duration = request.args.get("vibration-duration",type=int)
    pwm_value = request.args.get("pwm",type=int)
    nb_repetitions = request.args.get("nb-repetitions",type=int)
    time_between_vibration = request.args.get("time-between-vibration",type=int)

    if vibration_duration is None:
        abort(400, "vibration-duration must be an integer")
    if pwm_value is None or not 0 <= pwm_value <= 255:
        abort(400, "pwm must be an integer between 0 and 255")
    if nb_repetitions is None:
        abort(400, "nb-repetitions must be an integer")
    if time_between_vibration is None:
        abort(400, "time-between-vibration must be an integer")

    shared_haptic_service.vibration_to_serial(vibration_duration, pwm_value, nb_repetitions, time_between_vibration)

    return jsonify(status="ok",
                   action="vibration on",
                   vibration_duration=int(vibration_duration),
                   pwm=int(pwm_value),
                   nb_repetitions=int(nb_repetitions),
                   time_between_vibration=int(time_between_vibration))

