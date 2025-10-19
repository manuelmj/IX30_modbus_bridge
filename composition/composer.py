

# Domain interfaces
from domain.ports import ModbusServerPort, ModbusGpioClient, GPIOPort, ModbusOperations
from domain.models import ServiceType
# Infrastructure implementations (SOLO aquí se importan)
from infrastructure.modbus_server_adapter import ModbusServerAdapter
from infrastructure.gpio_modbus_client_adapter import ModbusGpioClientAdapter
from infrastructure.gpio_interface_adapter import DigiGPIOAdapter
from infrastructure.analog_modbus_client_interface import ModbusHoldingRegisterClientAdapter
from infrastructure.analog_interface_adapter import AnalogInterfaceAdapter
from infrastructure.utils import ModbusUtilities
# Application services
from application.gpio_modbus_handler import GPIOModbusHandler, GPIOSyncService
from application.analog_modbus_handler import AnalogModbusHandler, AnalogSyncService

from composition.config import ServiceConfig



class ServiceComposer:
    """
    COMPOSITION ROOT - Ensambla todas las dependencias.
    
    Es como tu services.py pero SOLO se encarga de crear y conectar,
    NO de ejecutar threading.
    """
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self._instances: dict[ServiceType, any] = {}
    
    # ============= INFRASTRUCTURE FACTORIES =============
    
    def create_modbus_server(self) -> ModbusServerPort:
        """Crear y configurar servidor Modbus."""
        if ServiceType.MODBUS_SERVER not in self._instances:
            self._instances[ServiceType.MODBUS_SERVER] = ModbusServerAdapter(
                self.config.server_ip, 
                self.config.server_port
            )
        return self._instances[ServiceType.MODBUS_SERVER]
    
    def create_gpio_modbus_client(self) -> ModbusGpioClient:
        """Crear y configurar cliente Modbus GPIO."""
        if ServiceType.GPIO_MODBUS_CLIENT not in self._instances:
            self._instances[ServiceType.GPIO_MODBUS_CLIENT] = ModbusGpioClientAdapter(
                self.config.client_ip,
                self.config.client_port
            )
        return self._instances[ServiceType.GPIO_MODBUS_CLIENT]
    
    def create_gpio_port(self) -> GPIOPort:
        """Crear puerto GPIO físico."""
        if ServiceType.GPIO_PORT not in self._instances:
            self._instances[ServiceType.GPIO_PORT] = DigiGPIOAdapter()
        return self._instances[ServiceType.GPIO_PORT]

    def create_analog_modbus_client(self):
        """Crear cliente Modbus analógico."""
        if ServiceType.ANALOG_MODBUS_CLIENT not in self._instances:
            self._instances[ServiceType.ANALOG_MODBUS_CLIENT] = ModbusHoldingRegisterClientAdapter(
                self.config.client_ip,
                self.config.client_port
            )
        return self._instances[ServiceType.ANALOG_MODBUS_CLIENT]

    def create_analog_port(self):
        """Crear puerto analógico."""
        if ServiceType.ANALOG_PORT not in self._instances:
            self._instances[ServiceType.ANALOG_PORT] = AnalogInterfaceAdapter()
        return self._instances[ServiceType.ANALOG_PORT]

    # ============= APPLICATION SERVICES COMPOSITION =============
    
    def create_gpio_sync_service(self) -> GPIOSyncService:
        """
        COMPOSICIÓN: Ensamblar servicio GPIO completo.
        
        Esto es equivalente a tu función start_gpio_modbus_client()
        pero SIN threading.
        """
        modbus_client = self.create_gpio_modbus_client()
        gpio_port = self.create_gpio_port()
        
        handler = GPIOModbusHandler(modbus_client, gpio_port)
        
        sync_service = GPIOSyncService(handler)
        
        return sync_service
    
    def create_analog_sync_service(self) -> AnalogSyncService:
        """
        COMPOSICIÓN: Ensamblar servicio analógico completo.
        
        Equivalente a tu start_register_modbus_client() pero SIN threading.
        """
        modbus_client = self.create_analog_modbus_client()
        analog_port = self.create_analog_port()
        operations = ModbusUtilities()
        
        handler = AnalogModbusHandler(modbus_client, analog_port, operations)
        
        sync_service = AnalogSyncService(handler)
        
        return sync_service
    
    # ============= COMPLETE APPLICATION COMPOSITION =============
    
    def create_complete_application(self):
        """
        Crear la aplicación completa ensamblada.
        
        Esto reemplaza la lógica de tus 3 funciones start_*
        pero devuelve objetos configurados en lugar de iniciar hilos.
        """
        return {
            ServiceType.MODBUS_SERVER: self.create_modbus_server(),
            ServiceType.GPIO_SYNC_SERVICE: self.create_gpio_sync_service(),
            ServiceType.ANALOG_SYNC_SERVICE: self.create_analog_sync_service()
        }
    
    def cleanup(self):
        """Limpiar recursos."""
        for instance in self._instances.values():
            if hasattr(instance, 'stop'):
                try:
                    instance.stop()
                except Exception:
                    pass




