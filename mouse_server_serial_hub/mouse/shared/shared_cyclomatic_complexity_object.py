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
                    cls._instance.pwm_nb_pulse_erm = 0
                    cls._instance.feedback_profile = None

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

    def get_pwm_nb_pulse_erm(self):
        return self.pwm_nb_pulse_erm

    def get_feedback_profile(self):
        with self.access_lock:
            return self.feedback_profile

    def get_report_state(self):
        with self.access_lock:
            return {
                "class_name": self.class_name,
                "method_name": self.method_name,
                "signature": self.signature,
                "complexity": self.cyclomatic_complexity,
                "feedback_profile": self.feedback_profile,
            }

    def update_report(self, class_name, method_name, signature, complexity, feedback_profile):
        with self.access_lock:
            self.class_name = class_name
            self.method_name = method_name
            self.signature = signature
            self.cyclomatic_complexity = complexity
            self.feedback_profile = feedback_profile

            thermal = feedback_profile["thermal"]
            vibration = feedback_profile["vibration"]
            self.pwm_value_thermal = thermal["pwm"] if thermal["enabled"] else 0
            self.pwm_value_erm = vibration["pwm"] if vibration["enabled"] else 0
            self.pwm_nb_pulse_erm = vibration["pulseCount"] if vibration["enabled"] else 0

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

    def set_pwm_nb_pulse_erm(self, pwm_nb_pulse_erm):
        self.pwm_nb_pulse_erm = pwm_nb_pulse_erm

    def set_feedback_profile(self, feedback_profile):
        with self.access_lock:
            self.feedback_profile = feedback_profile

