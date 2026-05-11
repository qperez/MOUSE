import threading


class SharedMouseState:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SharedMouseState, cls).__new__(cls)
                    cls._instance.access_lock = threading.Lock()
                    cls._instance.is_mouse_speed_activated = False
        return cls._instance

    def get_mouse_speed_state(self):
        return self.is_mouse_speed_activated

    def set_mouse_speed_state(self, state):
        self.is_mouse_speed_activated = state

