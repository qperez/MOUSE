import ctypes
import threading


class MouseSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def get_mouse_names():
        return ["Windows system mouse"]

    @staticmethod
    def get_mouse_id_with_name(device_name):
        if device_name != "Windows system mouse":
            raise RuntimeError(f"Any devices found with the name: {device_name}")
        return device_name, "windows-system-mouse"

    @staticmethod
    def set_xinput_mouse_id(mouse_id):
        if mouse_id != "windows-system-mouse":
            raise ValueError("Invalid Windows mouse identifier")

    @staticmethod
    def set_mouse_speed(factor):
        if not 0.1 <= factor <= 1:
            raise ValueError("Mouse speed factor must be between 0.1 and 1")

        windows_speed = round(1 + factor * 9)
        result = ctypes.windll.user32.SystemParametersInfoW(
            0x0071, 0, windows_speed, 0x0002
        )
        if not result:
            raise ctypes.WinError()