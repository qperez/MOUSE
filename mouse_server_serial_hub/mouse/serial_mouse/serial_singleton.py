import serial
import threading

class SerialSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, port='/dev/ttyACM1', baudrate=115200):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    try:
                        cls._instance.serial = serial.Serial(port,baudrate,timeout=1)
                        print("Serial port connected")
                    except serial.SerialException as e:
                        cls._instance.serial = None
                        print(f"Failed to open serial port: {e}")
                    cls._instance.access_lock = threading.Lock()
        return cls._instance

    def write_message(self, message):
        with self.access_lock:
            message = str(message) + '\n'
            self.serial.write(message.encode())