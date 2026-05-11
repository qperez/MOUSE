from flask import Blueprint, request, abort, jsonify

from phase_api.serial_mouse.mouse_singleton import MouseSingleton

mouse_singleton = MouseSingleton()
mouse_bp = Blueprint('mouse', __name__)

@mouse_bp.route("/names")
def get_mouse_names_rest():
    try:
        devices = mouse_singleton.get_mouse_names()
        return jsonify(status="ok", mouse_names=devices)
    except Exception as e:
        abort(400, str(e))

@mouse_bp.route("/set-name")
def set_mouse_id_with_name():
    mouse_name = request.args.get("mouse-name")
    try:
        mouse_name, id = mouse_singleton.get_mouse_id_with_name(mouse_name)
        mouse_singleton.set_xinput_mouse_id(id)
        return jsonify(status="ok", mouse_name=mouse_name, mouse_id=id)
    except Exception as e:
        abort(400, str(e))

@mouse_bp.route("/speed")
def mouse_speed():
    global is_mouse_speed_activated
    value = request.args.get("value")
    start = request.args.get("start")

    try:
        # Si le paramètre start est présent, activer ou désactiver avec des valeurs fixes
        if start is not None:
            if start == "1":
                is_mouse_speed_activated = True
            elif start == "0":
                is_mouse_speed_activated = False
                #set_mouse_speed(1)  # valeur arbitraire pour désactiver
            else:
                abort(400, "Invalid start value, must be 0 or 1")
            return jsonify(status="ok", action="start", start=int(start))

        # Sinon, régler la vitesse via 'value'
        if value is None:
            abort(400, "Missing value")
        mouse_singleton.set_mouse_speed(float(value))
        return jsonify(status="ok", value=float(value))

    except Exception as e:
        abort(400, str(e))
