from flask import Blueprint, request, abort, jsonify

from mouse_server_serial_hub.mouse.shared.shared_thermal_state import SharedThermalState
from mouse_server_serial_hub.mouse.shared.shared_haptic_service import SharedHapticService


thermal_bp = Blueprint('thermal', __name__)

shared_thermal_state = SharedThermalState()
shared_haptic_service = SharedHapticService()

@thermal_bp.route("/on")
def thermal_poweron():
    heating_duration = request.args.get("duration")
    pwm_value = request.args.get("pwm")

    shared_haptic_service.thermal_to_serial(heating_duration, pwm_value)

    return jsonify(status="ok", action="heat", duration=int(heating_duration), pwm=int(pwm_value))


@thermal_bp.route("/gui")
def thermal_gui():
    start = request.args.get("start")
    try:
        # Si le paramètre start est présent, activer ou désactiver avec des valeurs fixes
        if start is not None:
            if start == "1":
                shared_thermal_state.set_thermal_state_ide(False)
                shared_thermal_state.set_thermal_state_gui(True)
            elif start == "0":
                shared_thermal_state.set_thermal_state_gui(False)
                #set_mouse_speed(1)  # valeur arbitraire pour désactiver
            else:
                abort(400, "Invalid start value, must be 0 or 1")
            return jsonify(status="ok", action="start", start=int(start))
    except Exception as e:
        abort(400, str(e))

@thermal_bp.route("/ide")
def thermal_ide():
    start = request.args.get("start")
    try:
        # Si le paramètre start est présent, activer ou désactiver avec des valeurs fixes
        if start is not None:
            if start == "1":
                shared_thermal_state.set_thermal_state_gui(False)
                shared_thermal_state.set_thermal_state_ide(True)
            elif start == "0":
                shared_thermal_state.set_thermal_state_ide(False)
                #set_mouse_speed(1)  # valeur arbitraire pour désactiver
            else:
                abort(400, "Invalid start value, must be 0 or 1")
            return jsonify(status="ok", action="start", start=int(start))
    except Exception as e:
        abort(400, str(e))