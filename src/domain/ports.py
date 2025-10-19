from abc import ABC, abstractmethod
from typing import List
from .models import State, GpioDirection

class GPIOPort(ABC):
    """Puerto para interactuar con GPIO físico"""

    @abstractmethod
    def read(self, pin: int) -> State:
        pass

    @abstractmethod
    def write(self, pin: int, value: State) -> None:
        pass

    @abstractmethod
    def get_direction(self, pin: int) -> GpioDirection:
        pass
     
class AnalogPort(ABC):
    """Puerto para interactuar con puertos analógicos físicos"""
    @abstractmethod
    def read_analog(self, channel: int) -> float:
        pass


class ModbusOperations(ABC):
    @abstractmethod
    def convert_float_to_registers(self, value: float) -> List[int]:
        """Convertir un valor float a dos registros Modbus (16 bits cada uno)"""
        pass
    @abstractmethod
    def convert_registers_to_float(self, registers: List[int]) -> float:
        """Convertir dos registros Modbus (16 bits cada uno) a un valor float"""
        pass

class ModbusServerPort(ABC):
    """Puerto que expone el gateway por Modbus"""
    @abstractmethod
    def start(self):
        pass
    @abstractmethod
    def stop(self):
        pass

class ModbusGpioClient(ABC):
    """Cliente Modbus para interactuar con GPIO"""
    @abstractmethod
    def read_coil(self, address: int) -> bool:
        pass

    @abstractmethod
    def write_coil(self, address: int, value: bool) -> None:
        pass
 

class ModbusRegisterClient(ABC):
    """Cliente Modbus para interactuar con registros"""
 
    @abstractmethod
    def read_holding_registers_process(self, address: int, count: int = 1) -> list:
        """Leer múltiples holding registers"""
        pass
    @abstractmethod
    def write_holding_registers_process(self, address: int, value: List[int]) -> bool:
        """Escribir un valor a un holding register"""
        pass