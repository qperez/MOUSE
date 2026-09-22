from flask import Blueprint, abort, jsonify, request

from mouse_server_serial_hub.mouse.serial_mouse.serial_singleton import SerialSingleton

serial_bp = Blueprint("serial", __name__)
serial_singleton = SerialSingleton()


@serial_bp.route("/port", methods=["GET", "POST"])
def serial_port():
    if request.method == "GET":
        return jsonify(
            status="ok",
            port=serial_singleton.port,
            serial_connected=serial_singleton.serial is not None,
        )

    payload = request.get_json(silent=True) or {}
    port = payload.get("port")
    if port is None:
        port = request.args.get("port")

    try:
        connected = serial_singleton.reconfigure(port)
        return jsonify(
            status="ok" if connected else "error",
            port=serial_singleton.port,
            serial_connected=connected,
        ), 200 if connected else 400
    except (TypeError, ValueError) as error:
        abort(400, str(error))