from flask import Blueprint, request, abort, jsonify

from mouse_server_serial_hub.mouse.shared.shared_cyclomatic_complexity_object import SharedCyclomaticComplexityObject

from mouse_server_serial_hub.mouse.shared.shared_haptic_service import SharedHapticService
from mouse_server_serial_hub.mouse.serial_mouse.serial_singleton import SerialSingleton
from mouse_server_serial_hub.mouse.shared.shared_m5_state import SharedM5State

cyclomatic_complexity_bp = Blueprint('cyclomatic_complexity', __name__)
shared_cyclomatic_complexity_object = SharedCyclomaticComplexityObject()

shared_haptic_service = SharedHapticService()
shared_m5_state = SharedM5State()
serial_singleton = SerialSingleton()


@cyclomatic_complexity_bp.route("/gui")
def cyclo_gui():
    start = request.args.get("start",type=int)
    try:
        if start is not None:
            if start == 1:
                shared_m5_state.set_m5_gui_mode("cyclo")
                if serial_singleton is not None:
                    serial_singleton.write_message({"mode": "cyclo"})
                return jsonify(status="ok", action="start", start="cyclo")
            elif start == 0:
                shared_m5_state.set_m5_gui_mode("default")
                if serial_singleton is not None:
                    serial_singleton.write_message({"mode": "default"})
                return jsonify(status="ok", action="start", start="default")
            else:
                abort(400, "Invalid argument, must be 1 or 0")
    except Exception as e:
        abort(400, str(e))



@cyclomatic_complexity_bp.route("/complexity", methods=["POST"])
def receive_complexity():
    try:
        data = request.get_json(force=True)

        if data is None:
            abort(400, "Invalid JSON body")

        uri         = data.get("uri")
        class_name  = data.get("className")
        method_name = data.get("methodName")
        signature   = data.get("signature")
        complexity  = data.get("complexity")
        start_line  = data.get("startLine")

        shared_cyclomatic_complexity_object.set_class_name(class_name)
        shared_cyclomatic_complexity_object.set_method_name(method_name)
        shared_cyclomatic_complexity_object.set_signature(signature)
        shared_cyclomatic_complexity_object.set_cyclomatic_complexity(complexity)

        #    /**
        # * Return a human-readable risk label based on McCabe's thresholds.
        # * 1-5:   Simple, low risk
        # * 6-10:  Moderate complexity
        # * 11-20: High complexity, consider refactoring
        # * 20+:   Very high, untestable
        # */
        
        # TODO : tester valeurs et paramètres pour choix modalité (avec fichier de config plugin)
        if complexity <= 5:
            pwm_value_erm = 30
            pwm_nb_pulse_erm = 1
            pwm_value_thermal = 0
        elif 5 < complexity <= 10:
            pwm_value_erm = 50
            pwm_nb_pulse_erm = 2
            pwm_value_thermal = 0
        elif 10 < complexity <= 20:
            pwm_value_erm = 70
            pwm_nb_pulse_erm = 3
        else :
            pwm_value_erm = 90
            pwm_nb_pulse_erm = 3

        shared_cyclomatic_complexity_object.set_pwm_value_erm(pwm_value_erm)
        shared_cyclomatic_complexity_object.set_pwm_nb_pulse_erm(pwm_nb_pulse_erm)
        shared_cyclomatic_complexity_object.set_pwm_value_thermal(pwm_value_thermal)
        print(f"[complexity] {method_name} → {complexity} ) @ line {start_line}")
        print(signature)
        print(uri)

        return jsonify(status="ok", received=data), 200

    except Exception as e:
        abort(400, str(e))