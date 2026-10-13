from time import sleep
import platform
import psutil

from mouse_server_serial_hub.mouse.serial_mouse.serial_singleton import SerialSingleton
from mouse_server_serial_hub.mouse.shared.shared_m5_state import SharedM5State

serial_singleton = SerialSingleton()
shared_m5_state = SharedM5State()


def hardware_infos_over_serial_thread():
    rapl_energy_start = get_rapl_value()

    while True:
        # send cpu data to serial for default gui
        if shared_m5_state.get_m5_gui_mode() == "default" and serial_singleton is not None:
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
    if platform.system() == "Linux":
        with open("/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj") as f:
            return int(f.read())
    else :
         return 0 # TODO : windows version