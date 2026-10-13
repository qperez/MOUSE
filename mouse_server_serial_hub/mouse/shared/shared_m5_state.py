import threading

class SharedM5State:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SharedM5State, cls).__new__(cls)
                    cls._instance.access_lock = threading.Lock()
                    cls._instance.m5_gui_mode = "default"
        return cls._instance

    def get_m5_gui_mode(self):
        return self.m5_gui_mode

    def set_m5_gui_mode(self, mode):
        self.m5_gui_mode = mode

