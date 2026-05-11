import subprocess
import threading


class MouseSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # Garantit qu'une seule instance est créée (thread-safe)
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MouseSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Évite la réinitialisation multiple en environnement multi-thread
        if hasattr(self, "_initialized") and self._initialized:
            return

        name, device_id = self.get_mouse_id_with_name("PS/2 Generic Mouse")
        self.xinput_mouse_id = device_id

        self._initialized = True

    @staticmethod
    def get_mouse_names():
        return subprocess.check_output(
            ["xinput", "list", "--name-only"],
            text=True
        ).splitlines()

    def get_mouse_id_with_name(self, device_name_exact: str):
        devices = self.get_mouse_names()

        for name in devices:
            if name == device_name_exact:
                # On récupère l'ID avec la commande xinput --id-only
                device_id = subprocess.check_output(
                    ["xinput", "list", "--id-only", name],
                    text=True
                ).strip()
                return name, device_id

        raise RuntimeError(f"Any devices found with the name: {device_name_exact}")

    def set_xinput_mouse_id(self, mouse_id: str):
        self.xinput_mouse_id = mouse_id

    def set_mouse_speed(self, factor):
        factor = float(factor)

        # Set matrix factor for slowing or speeding the mouse
        matrix = [
            str(factor), "0"        , "0",
            "0"        , str(factor), "0",
            "0"        , "0"        , "1"
        ]

        # Ligne 1 : [factor, 0, 0]
        # - factor : Ajuste la vitesse horizontale (mouvement gauche/droite)
        # - 0 : Pas de rotation verticale
        # - 0 : Pas de translation verticale

        # Ligne 2 : [0, factor, 0]
        # - 0 : Pas de rotation horizontale
        # - factor : Ajuste la vitesse verticale (mouvement haut/bas)
        # - 0 : Pas de translation horizontale

        # Ligne 3 : [0, 0, 1]
        # - 0 : Pas de translation verticale
        # - 0 : Pas de translation horizontale
        # - 1 : Conserve la position (nécessaire pour la transformation)

        subprocess.call([
            "xinput", "set-prop",
            self.xinput_mouse_id,
            "Coordinate Transformation Matrix",
            *matrix
        ])