import threading
from domain.ports import AnalogPort
from digidevice import ain
from digidevice.ain import Name, Mode

ANALOG_MAP = {
    1: Name.ain1,
    2: Name.ain2,
    3: Name.ain3,
    4: Name.ain4,
}

# Lock global: la librería digidevice.ain no es thread-safe; serializa
# todos los accesos al hardware desde cualquier hilo.
_ain_lock = threading.Lock()


class AnalogInterfaceAdapter(AnalogPort):
    """Adaptador para interactuar con puertos analógicos físicos"""

    def __init__(self):
        # Cachear el modo de cada canal una sola vez para evitar llamadas
        # repetidas al hardware en cada muestra (ain.get_mode es costoso).
        self._mode_cache: dict = {
            ch: ain.get_mode(name) for ch, name in ANALOG_MAP.items()
        }

    def read_analog(self, channel: int) -> float:
        """
        Leer el valor analógico de un canal específico.
        Thread-safe: serializa el acceso al hardware ain con un lock global.

        Args:
            channel: Canal analógico a leer (1-4)

        Returns:
            float: Valor analógico leído
        """
        if channel not in ANALOG_MAP:
            raise ValueError(f"Canal analógico {channel} no válido. Debe ser 1-4")

        analog_name = ANALOG_MAP[channel]
        mode = self._mode_cache[channel]

        with _ain_lock:
            raw = ain.get_value(analog_name)

        if mode == Mode.voltage:
            return raw / 1000.0        # mV → V
        elif mode == Mode.current:
            return raw / 1000000.0     # uA → A
        else:
            raise ValueError(f"Modo analógico desconocido para el canal {channel}: {mode}")

    def get_voltage(self, channel: int) -> float:
        """
        Leer el valor de voltaje de un canal analógico específico.

        Args:
            channel: Canal analógico a leer (1-4)

        Returns:
            float: Valor de voltaje leído en Voltios
        """
        if channel not in ANALOG_MAP:
            raise ValueError(f"Canal analógico {channel} no válido. Debe ser 1-4")

        analog_name = ANALOG_MAP[channel]
        with _ain_lock:
            return ain.get_value(analog_name) / 1000.0  # Convertir de mV a V

    def get_current(self, channel: int) -> float:
        """
        Leer el valor de corriente de un canal analógico específico.

        Args:
            channel: Canal analógico a leer (1-4)
            
        Returns:
            float: Valor de corriente leído en Amperios
        """
        if channel not in ANALOG_MAP:
            raise ValueError(f"Canal analógico {channel} no válido. Debe ser 1-4")
        
        analog_name = ANALOG_MAP[channel]
        with _ain_lock:
            return ain.get_value(analog_name) / 1000000.0  # Convertir de uA a A