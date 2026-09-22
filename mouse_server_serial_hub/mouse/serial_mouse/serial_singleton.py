import serial
import threading
import platform


def default_port():
    if platform.system() == "Windows":
        return "COM3"
    if platform.system() == "Darwin":
        return "/dev/cu.usbmodem"
    return "/dev/ttyACM1"

class SerialSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, port=None, baudrate=115200):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.access_lock = threading.Lock()
                    cls._instance.port = port or default_port()
                    cls._instance.baudrate = baudrate
                    cls._instance._connect()
        return cls._instance

    def _connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Serial port connected: {self.port}")
        except serial.SerialException as error:
            self.serial = None
            print(f"Failed to open serial port {self.port}: {error}")

    def reconfigure(self, port):
        port = str(port).strip()
        if not port:
            raise ValueError("Serial port cannot be empty")

        with self.access_lock:
            if self.serial is not None:
                self.serial.close()
            self.port = port
            self._connect()
            return self.serial is not None

    def write_message(self, message):
        with self.access_lock:
            if self.serial is None:
                raise serial.SerialException(f"Serial port is not connected: {self.port}")
            message = str(message) + '\n'
            self.serial.write(message.encode())