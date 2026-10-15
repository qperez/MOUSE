from time import sleep

from mouse_server_serial_hub.mouse.serial_mouse.serial_singleton import SerialSingleton
from mouse_server_serial_hub.mouse.shared.shared_cyclomatic_complexity_object import SharedCyclomaticComplexityObject
from mouse_server_serial_hub.mouse.shared.shared_m5_state import SharedM5State
from mouse_server_serial_hub.mouse.shared.shared_haptic_service import SharedHapticService


serial_singleton = SerialSingleton()
shared_cyclomatic_complexity_object = SharedCyclomaticComplexityObject()
shared_m5_state = SharedM5State()
shared_haptic_service = SharedHapticService()


def cyclomatic_complexity_over_serial_thread():
    def current_state():
        report_state = shared_cyclomatic_complexity_object.get_report_state()
        json_values = {
            "class-name": report_state["class_name"],
            "method-name": report_state["method_name"],
            "signature": report_state["signature"],
            "cyclomatic-complexity": report_state["complexity"],
        }
        feedback = report_state["feedback_profile"]
        return json_values, (tuple(json_values.items()), feedback)

    _, last_state = current_state()

    while True:
        if shared_m5_state.get_m5_gui_mode() == "cyclo" and serial_singleton is not None:
            json_values, state = current_state()
            feedback = state[1]
            if state != last_state:
                last_state = state
                serial_singleton.write_message(json_values)

                if feedback["active"]:
                    thermal = feedback["thermal"]
                    if thermal["enabled"]:
                        shared_haptic_service.thermal_to_serial(
                            thermal["durationMs"], thermal["pwm"]
                        )
                    vibration = feedback["vibration"]
                    if vibration["enabled"]:
                        shared_haptic_service.vibration_to_serial(
                            vibration["durationMs"],
                            vibration["pwm"],
                            vibration["pulseCount"],
                            vibration["pulseDelayMs"],
                        )

        sleep(0.5)