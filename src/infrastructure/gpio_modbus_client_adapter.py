import logging
from typing import Optional
from domain.ports import ModbusGpioClient
# Importar pymodbus dinámicamente
from pymodbus.client import ModbusTcpClient

_logger = logging.getLogger(__name__)

class ModbusClientError(Exception):
    """Excepción específica para errores del cliente Modbus"""
    pass

class ModbusGpioClientAdapter(ModbusGpioClient):
    """
    Adaptador cliente Modbus para interactuar con GPIO.
    
    Permite leer y escribir coils Modbus que representan estados de GPIO.
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
        
        _logger.info(f"Adaptador GPIO Modbus inicializado para {self.ip}:{self.port}")

    def read_coil(self, address: int) -> bool:
        """
        Leer el estado de un coil Modbus.
        
        Args:
            address: Dirección del coil a leer
            
        Returns:
            bool: Estado del coil (True/False)
            
        Raises:
            ModbusClientError: Si ocurre un error en la comunicación
            ValueError: Si la dirección no es válida
        """
        if not isinstance(address, int) or address < 0:
            raise ValueError(f"Dirección inválida: {address}")
                    
        _logger.debug(f"Leyendo coil en dirección {address}")
        
        try:
            self.connect()
            result = self.client.read_coils(address, count=1)
            if result.isError():
                error_msg = f"Error leyendo coil en address {address}: {result}"
                _logger.error(error_msg)
                raise ModbusClientError(error_msg)
            
            value = result.bits[0]
            _logger.debug(f"Coil {address} leído: {value}")
            return value
            
        except Exception as e:
            error_msg = f"Excepción leyendo coil {address}: {str(e)}"
            _logger.error(error_msg)
            raise ModbusClientError(error_msg) from e

    def write_coil(self, address: int, value: bool) -> None:
        """
        Escribir un valor a un coil Modbus.
        
        Args:
            address: Dirección del coil a escribir
            value: Valor a escribir (True/False)
            
        Raises:
            ModbusClientError: Si ocurre un error en la comunicación
            ValueError: Si la dirección no es válida
        """
        if not isinstance(address, int) or address < 0:
            raise ValueError(f"Dirección inválida: {address}")
            
        if not isinstance(value, bool):
            raise ValueError(f"Valor debe ser booleano, recibido: {type(value)}")
                  
        _logger.debug(f"Escribiendo coil {address} = {value}")
        
        try:
            self.connect()
            result = self.client.write_coil(address, value)
            if result.isError():
                error_msg = f"Error escribiendo coil en address {address}: {result}"
                _logger.error(error_msg)
                raise ModbusClientError(error_msg)
                
            _logger.debug(f"Coil {address} escrito exitosamente: {value}")
            
        except Exception as e:
            error_msg = f"Excepción escribiendo coil {address}: {str(e)}"
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
    
    