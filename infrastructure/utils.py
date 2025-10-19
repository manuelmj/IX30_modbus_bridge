from pymodbus.client import ModbusTcpClient
from domain.ports import ModbusOperations


class ModbusUtilities(ModbusOperations): 
    # --- utilidades para float32 ---
    
    def convert_registers_to_float(self, registers: list[int]) -> float:
        decoder = ModbusTcpClient.convert_from_registers(
            registers,
            data_type= ModbusTcpClient.DATATYPE.FLOAT32,
            word_order='big'
        )
        return decoder

    def convert_float_to_registers(self, value: float) -> list[int]:
        builder = ModbusTcpClient.convert_to_registers(
            value, data_type=ModbusTcpClient.DATATYPE.FLOAT32, word_order='big'
            )

        return builder

