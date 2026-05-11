import threading

import psutil
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from phase_api.controllers.cyclomatic_complexity_controller import cyclomatic_complexity_bp
from phase_api.controllers.mouse_controller import mouse_bp
from phase_api.controllers.thermal_controller import thermal_bp
from phase_api.serial_mouse.serial_singleton import SerialSingleton
from phase_api.services.cyclomatic_complexity_service import cyclomatic_complexity_over_serial_thread
from phase_api.services.mouse_service import mouse_speed_thread
from phase_api.services.thermal_service import hardware_infos_over_serial_thread
from phase_api.shared.shared_thermal_state import SharedThermalState

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
serial_singleton = SerialSingleton()

def send_cpu():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        socketio.emit("system_status", {
            "cpu": cpu,
            "serial_connected": (serial_singleton.serial is not None)
        })
        socketio.sleep(1)

@socketio.on("connect")
def handle_connect():
    print("Client connected")

    socketio.emit("system_status", {
        "cpu": psutil.cpu_percent(),
        "serial_connected": (serial_singleton.serial is not None)
    })


if __name__ == "__main__":
    app.register_blueprint(thermal_bp, url_prefix="/thermal")
    app.register_blueprint(mouse_bp, url_prefix="/mouse")
    app.register_blueprint(cyclomatic_complexity_bp)

    ms_speed_thread = threading.Thread(target=mouse_speed_thread)
    ms_speed_thread.start()

    hw_infos_over_serial_thread = threading.Thread(target=hardware_infos_over_serial_thread)
    hw_infos_over_serial_thread.start()

    cyclomatic_complexity_over_serial_thread = threading.Thread(target=cyclomatic_complexity_over_serial_thread)
    cyclomatic_complexity_over_serial_thread.start()

    shared_thermal_state = SharedThermalState()
    shared_thermal_state.set_thermal_state_ide(True)

    socketio.start_background_task(send_cpu)
    socketio.run(app, host="127.0.0.1", port=5000, allow_unsafe_werkzeug=True, debug=True)