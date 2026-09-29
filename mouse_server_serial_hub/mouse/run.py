import argparse
import threading

import psutil
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

serial_singleton = None


def parse_args():
    parser = argparse.ArgumentParser(description="Run the MOUSE server")
    parser.add_argument(
        "--serial-port",
        default=None,
        help="Serial port for the M5Stack, for example COM5 or /dev/ttyACM1",
    )
    return parser.parse_args()


def send_cpu():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        socketio.emit("system_status", {
            "cpu": cpu,
            "serial_connected": (serial_singleton is not None and serial_singleton.serial is not None)
        })
        socketio.sleep(1)

@socketio.on("connect")
def handle_connect():
    print("Client connected")

    socketio.emit("system_status", {
        "cpu": psutil.cpu_percent(),
        "serial_connected": (serial_singleton is not None and serial_singleton.serial is not None)
    })


if __name__ == "__main__":
    args = parse_args()

    from mouse_server_serial_hub.mouse.serial_mouse.serial_singleton import SerialSingleton

    serial_singleton = SerialSingleton(port=args.serial_port)

    from mouse_server_serial_hub.mouse.controllers.erm_controller import vibration_bp
    from mouse_server_serial_hub.mouse.controllers.thermal_controller import thermal_bp
    from mouse_server_serial_hub.mouse.controllers.mouse_controller import mouse_bp
    from mouse_server_serial_hub.mouse.controllers.serial_controller import serial_bp
    from mouse_server_serial_hub.mouse.controllers.cyclomatic_complexity_controller import cyclomatic_complexity_bp

    from mouse_server_serial_hub.mouse.services.mouse_service import mouse_speed_thread

    from mouse_server_serial_hub.mouse.shared.shared_haptic_service import SharedHapticService

    from mouse_server_serial_hub.mouse.services.cyclomatic_complexity_service import cyclomatic_complexity_over_serial_thread
    from mouse_server_serial_hub.mouse.services.live_cpu_service import hardware_infos_over_serial_thread


    app.register_blueprint(serial_bp, url_prefix="/serial")
    app.register_blueprint(mouse_bp, url_prefix="/mouse")
    app.register_blueprint(cyclomatic_complexity_bp, url_prefix="/metric")
    app.register_blueprint(vibration_bp, url_prefix="/vibration")
    app.register_blueprint(thermal_bp, url_prefix="/thermal")


    ms_speed_thread = threading.Thread(target=mouse_speed_thread)
    ms_speed_thread.start()

    hw_infos_over_serial_thread = threading.Thread(target=hardware_infos_over_serial_thread)
    hw_infos_over_serial_thread.start()

    cyclomatic_complexity_over_serial_thread = threading.Thread(target=cyclomatic_complexity_over_serial_thread)
    cyclomatic_complexity_over_serial_thread.start()


    shared_haptic_service = SharedHapticService()
    shared_haptic_service.set_thermal_state(True)
    shared_haptic_service.set_vibration_state(True)

    socketio.start_background_task(send_cpu)
    socketio.run(
        app,
        host="127.0.0.1",
        port=5000,
        allow_unsafe_werkzeug=True,
        debug=True,
        use_reloader=False,  # reloader is disabled to prevent multiple mouse-speed workers  
    )