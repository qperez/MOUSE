from time import sleep

from mouse_server_serial_hub.mouse.serial_mouse.serial_singleton import SerialSingleton
from mouse_server_serial_hub.mouse.shared.shared_cyclomatic_complexity_object import SharedCyclomaticComplexityObject
from mouse_server_serial_hub.mouse.shared.shared_thermal_state import SharedThermalState

serial_singleton = SerialSingleton()
shared_thermal_state = SharedThermalState()
shared_cyclomatic_complexity_object = SharedCyclomaticComplexityObject()

def cyclomatic_complexity_over_serial_thread():
    json_values = {
        "class-name": "",
        "method-name": "",
        "signature": "",
        "cyclomatic-complexity": "",
        "pwm-value-thermal": 0,
        "pwm-value-erm": 0,
        "pwm_nb_pulse_erm": 0
    }

    while True:
        if shared_thermal_state.get_thermal_state_ide() and serial_singleton is not None:
                if json_values["signature"] != shared_cyclomatic_complexity_object.get_signature():
                    json_values = {
                        "class-name" : shared_cyclomatic_complexity_object.get_class_name(),
                        "method-name" : shared_cyclomatic_complexity_object.get_method_name(),
                        "signature" : shared_cyclomatic_complexity_object.get_signature(),
                        "cyclomatic-complexity" : shared_cyclomatic_complexity_object.get_cyclomatic_complexity(),
                        "pwm-value-thermal" : shared_cyclomatic_complexity_object.get_pwm_value_thermal(),
                        "pwm-value-erm": shared_cyclomatic_complexity_object.get_pwm_value_erm(),
                        "pwm-nb-pulse-erm":shared_cyclomatic_complexity_object.get_pwm_nb_pulse_erm()
                    }
                    serial_singleton.write_message(json_values)
        sleep(0.5)