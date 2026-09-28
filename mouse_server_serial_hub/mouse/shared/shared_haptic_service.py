import threading

from mouse_server_serial_hub.mouse.serial_mouse.serial_singleton import SerialSingleton
serial_singleton = SerialSingleton()


class SharedHapticService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SharedHapticService, cls).__new__(cls)
                    cls._instance.access_lock = threading.Lock()
                    cls._instance.thermal_state = 0
                    cls._instance.vibration_state = 0
        return cls._instance


    def get_thermal_state(self):
        return self.thermal_state

    def get_vibration_state(self):
        return self.vibration_state

    def set_thermal_state(self, thermal_state):
        self.thermal_state = thermal_state

    def set_vibration_state(self, vibration_state):
        self.vibration_state = vibration_state


    def vibration_to_serial(self, duration = 100, pwm = 100, pulse = 1, delay = 0):
        if not self.vibration_state: 
            print("vibration is not active")
            return
            
        json_values = {
                "pwm_duration_erm": duration,
                "pwm_value_erm": pwm,
                "pwm_nb_pulse_erm": pulse,
                "pwm_pulse_delay_erm" : delay
        }

        print(json_values)

        if serial_singleton is not None:
            serial_singleton.write_message(json_values)


    def thermal_to_serial(self, duration = 1000, pwm = 100):
        if not self.thermal_state:
            print("thermal is not active")
            return

        json_values = {
                "pwm_duration_thermal": duration,
                "pwm_value_thermal": pwm,
        }

        print(json_values)

        if serial_singleton is not None:
            serial_singleton.write_message(json_values)
