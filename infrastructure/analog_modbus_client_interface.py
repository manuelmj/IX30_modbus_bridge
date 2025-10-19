from domain.ports import ModbusRegisterClient


import logging
from typing import Optional
from domain.ports import ModbusGpioClient
# Importar pymodbus dinámicamente
from pymodbus.client import ModbusTcpClient
from typing import List

_logger = logging.getLogger(__name__)

class ModbusClientError(Exception):
    """Excepción específica para errores del cliente Modbus"""
    pass

class ModbusHoldingRegisterClientAdapter(ModbusRegisterClient):
    """
    Adaptador cliente Modbus para interactuar con Holding Registers.
    
    Permite leer y escribir holding registers Modbus.
    El adaptador maneja internamente la creación y gestión del cliente Modbus TCP.
    """
    
    def __init__(self, ip: str, port: int = 502):  
        """
        Inicializar el adaptador con parámetros de conexión.
        
        Args:
            ip (str): Dirección IP del servidor Modbus
            port (int): Puerto del servidor Modbus (por defecto 502)
            
        Raises:
            ValueError: Si los parámetros no son válidos
        """
        if not isinstance(ip, str) or not ip.strip():
            raise ValueError("La IP debe ser una cadena no vacía")
            
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ValueError("El puerto debe ser un entero entre 1 y 65535")
            
        self.ip = ip.strip()
        self.port = port
        self.client: Optional[object] = None
        self._connected = False
        
        _logger.info(f"Adaptador Holding Register Modbus inicializado para {self.ip}:{self.port}")

    def read_holding_registers_process(self, address: int, count: int = 1) -> list:
        """
        Leer uno o más holding registers Modbus.
        
        Args:
            address: Dirección del primer register a leer
            count: Número de registers a leer (por defecto 1)
            
        Returns:
            list: Lista de valores de los registers leídos
            
        Raises:
            ModbusClientError: Si ocurre un error en la comunicación
            ValueError: Si la dirección o count no son válidos
        """
        if not isinstance(address, int) or address < 0:
            raise ValueError(f"Dirección inválida: {address}")
        
        if not isinstance(count, int) or count < 1:
            raise ValueError(f"Count inválido: {count}")
                    
        _logger.debug(f"Leyendo {count} holding register(s) desde dirección {address}")
        
        try:
            self.connect()
            result = self.client.read_holding_registers(address, count=count)
            if result.isError():
                error_msg = f"Error leyendo holding register en address {address}: {result}"
                _logger.error(error_msg)
                raise ModbusClientError(error_msg)
            
            values = result.registers
            _logger.debug(f"Holding registers {address}-{address+count-1} leídos: {values}")
            return values
            
        except Exception as e:
            error_msg = f"Excepción leyendo holding register {address}: {str(e)}"
            _logger.error(error_msg)
            raise ModbusClientError(error_msg) from e

    def write_holding_registers_process(self, address: int, values: List[int]) -> bool:
        """
        Escribir un valor a un holding register Modbus.
        
        Args:
            address: Dirección del register a escribir
            value: Valor a escribir (0-65535)
            
        Raises:
            ModbusClientError: Si ocurre un error en la comunicación
            ValueError: Si la dirección o valor no son válidos
        """
        if not isinstance(address, int) or address < 0:
            raise ValueError(f"Dirección inválida: {address}")
                              
        _logger.info(f"Escribiendo holding register {address} = {values}")
        
        try:
            self.connect()
            result = self.client.write_registers(address=address, values=values)
            if result.isError():
                error_msg = f"Error escribiendo holding register en address {address}: {result}"
                _logger.error(error_msg)
                raise ModbusClientError(error_msg)
                
            _logger.debug(f"Holding register {address} escrito exitosamente: {values}")

            return True          
        except Exception as e:
            error_msg = f"Excepción escribiendo holding register {address}: {str(e)}"
            _logger.error(error_msg)
            raise ModbusClientError(error_msg) from e

   
    def connect(self) -> None:
        """
        Iniciar el cliente Modbus y establecer conexión.
        
        Crea internamente un ModbusTcpClient con la IP y puerto especificados
        en el constructor y establece la conexión.
        
        Raises:
            ModbusClientError: Si no se puede establecer la conexión
            ImportError: Si pymodbus no está instalado
        """
        if self._connected:
            _logger.warning("Cliente Modbus ya está conectado")
            return
            
        _logger.info(f"Iniciando cliente Modbus TCP para {self.ip}:{self.port}...")
        
        try:
            # Crear cliente Modbus TCP
            self.client = ModbusTcpClient(
                host=self.ip, 
                port=self.port,
                timeout=5,  # Timeout de 5 segundos
                retries=3   # Reintentos automáticos
            )
            
            # Establecer conexión
            connection_result = self.client.connect()
            if not connection_result:
                raise ModbusClientError(
                    f"No se pudo conectar al servidor Modbus en {self.ip}:{self.port}"
                )
            
            self._connected = True
            _logger.info(f"Cliente Modbus conectado exitosamente a {self.ip}:{self.port}")
            
        except ImportError as e:
            error_msg = "pymodbus no está instalado. Instalar con: pip install pymodbus"
            _logger.error(error_msg)
            raise ModbusClientError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Error iniciando cliente Modbus para {self.ip}:{self.port}: {str(e)}"
            _logger.error(error_msg)
            raise ModbusClientError(error_msg) from e

    def disconnect(self) -> None:
        """Cerrar la conexión Modbus"""
        if self.client and self._connected:
            self.client.close()
            self._connected = False
            _logger.info("Conexión Modbus cerrada")

    def __del__(self):
        """Destructor para asegurar que se cierra la conexión"""
        self.disconnect()