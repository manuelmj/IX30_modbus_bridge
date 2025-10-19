from domain.ports import AnalogPort
from digidevice import ain
from digidevice.ain import Name, Mode

ANALOG_MAP = {
    1: Name.ain1,
    2: Name.ain2,
    3: Name.ain3,
    4: Name.ain4,
}

class AnalogInterfaceAdapter(AnalogPort):
    """Adaptador para interactuar con puertos analógicos físicos"""

    def read_analog(self, channel: int) -> float:
        """
        Leer el valor analógico de un canal específico.

        Args:
            channel: Canal analógico a leer (1-4)

        Returns:
            float: Valor analógico leído
        """
        if channel not in ANALOG_MAP:
            raise ValueError(f"Canal analógico {channel} no válido. Debe ser 1-4")
        
        analog_name = ANALOG_MAP[channel]  # Name.ain1, Name.ain2, etc.
        mode = ain.get_mode(analog_name)
        
        if mode == Mode.voltage:
            value = self.get_voltage(channel)
        elif mode == Mode.current:
            value = self.get_current(channel)
        else:
            raise ValueError(f"Modo analógico desconocido para el canal {channel}: {mode}")

        return value

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
        return ain.get_value(analog_name) / 1000000.0  # Convertir de uA a A