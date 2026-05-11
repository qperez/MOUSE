from flask import Blueprint, request, abort, jsonify

from phase_api.services.cyclomatic_complexity_service import shared_cyclomatic_complexity_object
from phase_api.services.thermal_service import shared_thermal_state
from phase_api.shared.shared_cyclomatic_complexity_object import SharedCyclomaticComplexityObject
from phase_api.shared.shared_thermal_state import SharedThermalState

cyclomatic_complexity_bp = Blueprint('cyclomatic_complexity', __name__)
shared_cyclomatic_complexity_object = SharedCyclomaticComplexityObject()
shared_thermal_state = SharedThermalState()

@cyclomatic_complexity_bp.route("/complexity", methods=["POST"])
def receive_complexity():
    try:
        data = request.get_json(force=True)

        if data is None:
            abort(400, "Invalid JSON body")

        shared_thermal_state.set_thermal_state_gui(False)
        shared_thermal_state.set_thermal_state_ide(True)

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

        # Traitement ici (log, BDD, broadcast WebSocket…)
        print(f"[complexity] {method_name} → {complexity} ) @ line {start_line}")
        print(signature)
        print(uri)

        return jsonify(status="ok", received=data), 200

    except Exception as e:
        abort(400, str(e))