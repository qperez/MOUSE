from flask import Blueprint, request, abort, jsonify

from mouse_server_serial_hub.mouse.shared.shared_thermal_state import SharedThermalState

vibration_bp = Blueprint('vibration', __name__)

shared_thermal_state = SharedThermalState()

@vibration_bp.route("/on")
def on():
    vibration_duration = request.args.get("duration")
    pwm_value = request.args.get("pwm")
    return jsonify(status="ok", action="vibration on", duration=int(vibration_duration), pwm=int(pwm_value))

@vibration_bp.route("/loop")
def loop():
    vibration_duration = request.args.get("vibration-duration")
    pwm_value = request.args.get("pwm")
    nb_repetitions = request.args.get("nb-repetitions")
    time_between_vibration = request.args.get("time-between-vibration")
    return jsonify(status="ok",
                   action="vibration on",
                   vibration_duration=int(vibration_duration),
                   pwm=int(pwm_value),
                   nb_repetitions=int(nb_repetitions),
                   time_between_vibration=int(time_between_vibration))

