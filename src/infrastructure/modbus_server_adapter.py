
# import threading
import time
from pymodbus.datastore import ModbusServerContext, ModbusSequentialDataBlock, ModbusSimulatorContext
from pymodbus.server import StartTcpServer
# from pymodbus.client import ModbusTcpClient
from pymodbus.datastore import (
    ModbusServerContext,
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
)
from domain.ports import ModbusServerPort
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

_logger = logging.getLogger(__name__)
_logger.setLevel("INFO")





class ModbusServerAdapter(ModbusServerPort):
    """Adaptador para el servidor Modbus"""
    def __init__(self, ip: str, port: int):       
        self.ip = ip
        self.port = port
        self.context = self.setup_server()
        self.running = False

    def start(self):
        """Iniciar el servidor Modbus"""
        self.running = True
        while self.running:  # Cambiado a self.running
            try:
                self.servidor(self.context, self.ip, self.port)
            except Exception as e:
                _logger.error(f"Error en el servidor Modbus: {e}")
            finally:
                time.sleep(5)  # Esperar antes de reintentar

    def stop(self):
        """Detener el servidor Modbus"""
        self.running = False


    def setup_server(self):
        """Run server setup."""        
        context = ModbusDeviceContext(
            hr= ModbusSequentialDataBlock(40001, [0] * 10),
            co= ModbusSequentialDataBlock(1, [0] * 10),
            )
        single = True
            # Build data storage
        context = ModbusServerContext(devices=context, single=single)
        _logger.info("Server context ready") 
        return context


    def servidor(self, context, ip, port) -> None:
        """Run server."""
        txt = f"### start SYNC server, listening on {port} - {ip}"
        _logger.info(txt)
        
        _logger.info(f"### start SYNC server, listening on {port} - {ip}")
        StartTcpServer(
            context= context,  # Data storage
            # identity=context,  # server identify
            address=(ip,port),  # listen address
            # custom_functions=[],  # allow custom handling
            # framer=args.framer,  # The framer strategy to use
            # ignore_missing_devices=True,  # ignore request to a missing device
            # broadcast_enable=False,  # treat device_id 0 as broadcast address,
            # timeout=30,  # waiting time for request to complete
        )
        _logger.info("Server shutdown")








    # # --- utilidades para float32 ---
    # def registers_to_float(registers: list[int]) -> float:
    #     decoder = ModbusTcpClient.convert_from_registers(
    #         registers,
    #         data_type= ModbusTcpClient.DATATYPE.FLOAT64,
    #         word_order='big'
    #     )
    #     return decoder


    # def float_to_registers(value: float) -> list[int]:
    #     builder = ModbusTcpClient.convert_to_registers(
    #         value, data_type=ModbusTcpClient.DATATYPE.FLOAT32, word_order='big'
    #         )
    
    #     return builder



