from flask import Blueprint, request, abort, jsonify

from mouse_server_serial_hub.mouse.shared.shared_cyclomatic_complexity_object import SharedCyclomaticComplexityObject

from mouse_server_serial_hub.mouse.shared.shared_haptic_service import SharedHapticService
from mouse_server_serial_hub.mouse.serial_mouse.serial_singleton import SerialSingleton
from mouse_server_serial_hub.mouse.shared.shared_m5_state import SharedM5State
from mouse_server_serial_hub.mouse.shared.shared_mouse_state import SharedMouseState
from mouse_server_serial_hub.mouse.shared.feedback_profiles import (
    leave_feedback_profile,
    select_feedback_profile,
)

cyclomatic_complexity_bp = Blueprint('cyclomatic_complexity', __name__)
shared_cyclomatic_complexity_object = SharedCyclomaticComplexityObject()

shared_haptic_service = SharedHapticService()
shared_m5_state = SharedM5State()
serial_singleton = SerialSingleton()
shared_mouse_state = SharedMouseState()


@cyclomatic_complexity_bp.route("/gui")
def cyclo_gui():
    start = request.args.get("start",type=int)
    if start is None:
        abort(400, "start must be 0 or 1")
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

        if not isinstance(data, dict):
            abort(400, "Invalid JSON body")

        uri         = data.get("uri")
        class_name  = data.get("className")
        method_name = data.get("methodName")
        signature   = data.get("signature")
        complexity  = data.get("complexity")
        start_line  = data.get("startLine")
        event = data.get("event", "enter")
        feedback_settings = data.get("feedbackSettings")

        if event not in ("enter", "leave"):
            abort(400, "event must be 'enter' or 'leave'")
        if feedback_settings is None:
            abort(400, "feedbackSettings is required")
        if isinstance(complexity, bool) or not isinstance(complexity, int) or complexity < 0:
            abort(400, "complexity must be a non-negative integer")
        try:
            feedback_profile = (
                leave_feedback_profile()
                if event == "leave"
                else select_feedback_profile(complexity, feedback_settings)
            )
        except ValueError as error:
            abort(400, str(error))

        shared_cyclomatic_complexity_object.update_report(
            class_name,
            method_name,
            signature,
            complexity,
            feedback_profile,
        )
        mouse_speed = feedback_profile["mouseSpeed"]
        shared_mouse_state.set_mouse_speed_factor(
            mouse_speed["factor"]
            if feedback_profile["active"] and mouse_speed["enabled"]
            else 1.0
        )
        print(f"[complexity] {method_name} → {complexity} ) @ line {start_line}")
        print(signature)
        print(uri)

        return jsonify(status="ok", received=data), 200

    except (TypeError, ValueError) as error:
        abort(400, str(error))