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
    json_values = {
        "class-name": "",
        "method-name": "",
        "signature": "",
        "cyclomatic-complexity": ""
    }

    while True:
        if shared_m5_state.get_m5_gui_mode() == "cyclo" and serial_singleton is not None:
                if json_values["signature"] != shared_cyclomatic_complexity_object.get_signature():
                    json_values = {
                        "class-name" : shared_cyclomatic_complexity_object.get_class_name(),
                        "method-name" : shared_cyclomatic_complexity_object.get_method_name(),
                        "signature" : shared_cyclomatic_complexity_object.get_signature(),
                        "cyclomatic-complexity" : shared_cyclomatic_complexity_object.get_cyclomatic_complexity(),
                    }
                    serial_singleton.write_message(json_values)

                    shared_haptic_service.thermal_to_serial(shared_cyclomatic_complexity_object.get_pwm_value_thermal())
                    shared_haptic_service.vibration_to_serial(
                        200,
                        shared_cyclomatic_complexity_object.get_pwm_value_erm(),
                        shared_cyclomatic_complexity_object.get_pwm_nb_pulse_erm(),
                        200
                        ) #TODO : meilleur gestion du feedback

        sleep(0.5)