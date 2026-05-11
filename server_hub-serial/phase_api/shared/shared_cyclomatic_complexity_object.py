import threading


class SharedCyclomaticComplexityObject:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SharedCyclomaticComplexityObject, cls).__new__(cls)
                    cls._instance.access_lock = threading.Lock()
                    cls._instance.class_name = ""
                    cls._instance.method_name = ""
                    cls._instance.signature = ""
                    cls._instance.cyclomatic_complexity = 0
                    cls._instance.pwm_value_thermal = 0
                    cls._instance.pwm_value_erm = 0

        return cls._instance

    def get_class_name(self):
        return self.class_name

    def get_method_name(self):
        return self.method_name

    def get_signature(self):
        return self.signature

    def get_cyclomatic_complexity(self):
        return self.cyclomatic_complexity

    def get_pwm_value_thermal(self):
        return self.pwm_value_thermal

    def get_pwm_value_erm(self):
        return self.pwm_value_erm

    def set_class_name(self, class_name):
        self.class_name = class_name

    def set_method_name(self, method_name):
        self.method_name = method_name

    def set_cyclomatic_complexity(self, cyclomatic_complexity):
        self.cyclomatic_complexity = cyclomatic_complexity

    def set_signature(self, signature):
        self.signature = signature

    def set_pwm_value_thermal(self, pwm_value_thermal):
        self.pwm_value_thermal = pwm_value_thermal

    def set_pwm_value_erm(self, pwm_value_erm):
        self.pwm_value_erm = pwm_value_erm


