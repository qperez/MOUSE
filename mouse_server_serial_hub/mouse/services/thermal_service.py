from time import sleep

import psutil

from mouse_server_serial_hub.mouse.serial_mouse.serial_singleton import SerialSingleton
from mouse_server_serial_hub.mouse.shared.shared_thermal_state import SharedThermalState

serial_singleton = SerialSingleton()
shared_thermal_state = SharedThermalState()

def hardware_infos_over_serial_thread():
    rapl_energy_start = get_rapl_value()

    while True:
        if shared_thermal_state.get_thermal_state_gui() and serial_singleton is not None:
                values = build_metrics(rapl_energy_start)
                serial_singleton.write_message(values)
        sleep(0.5)

def build_metrics(rapl_start):
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent

    rapl_current = get_rapl_value()
    energy = round(((rapl_current - rapl_start) / 1_000_000) / 3600, 2)

    dict_json_data = {'cpu-load': cpu, 'memory-load': memory, 'cpu-energy': energy}
    return str(dict_json_data)

def get_rapl_value():
    with open("/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj") as f:
        return int(f.read())
