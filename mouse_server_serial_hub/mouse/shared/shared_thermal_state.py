import threading


class SharedThermalState:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SharedThermalState, cls).__new__(cls)
                    cls._instance.access_lock = threading.Lock()
                    cls._instance.is_thermal_gui_activated = False
                    cls._instance.is_thermal_ide_activated = False
        return cls._instance

    def get_thermal_state_gui(self):
        return self.is_thermal_gui_activated

    def get_thermal_state_ide(self):
        return self.is_thermal_ide_activated

    def set_thermal_state_gui(self, state):
        self.is_thermal_gui_activated = state

    def set_thermal_state_ide(self, state):
        self.is_thermal_ide_activated = state

