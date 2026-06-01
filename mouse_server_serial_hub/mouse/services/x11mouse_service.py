from time import sleep

import psutil

from mouse_server_serial_hub.mouse.serial_mouse.x11mouse_singleton import MouseSingleton
from mouse_server_serial_hub.mouse.shared.shared_mouse_state import SharedMouseState

mouse_singleton = MouseSingleton()
shared_mouse_state = SharedMouseState()

def mouse_speed_thread():
    while True:
        if shared_mouse_state.get_mouse_speed_state():
            cpu_load_percent = psutil.cpu_percent()
            mouse_speed_value = max(0.10, 1 - cpu_load_percent / 100)
            print(mouse_speed_value)
            mouse_singleton.set_mouse_speed(mouse_speed_value)
        else :
            mouse_singleton.set_mouse_speed(1)
        sleep(1)