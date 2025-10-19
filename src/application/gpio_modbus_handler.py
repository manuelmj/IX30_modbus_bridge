import logging
from typing import Dict
from domain.ports import ModbusGpioClient, GPIOPort
from domain.models import State, GpioDirection
import time

_logger = logging.getLogger(__name__)

class GPIOModbusHandler:
    """
    Manejador que integra GPIO físico con cliente Modbus.
    
    Esta clase actúa como orquestador entre el GPIO físico y el cliente Modbus,
    permitiendo sincronizar estados y controlar dispositivos remotamente.
    """
    
    def __init__(self, modbus_client: ModbusGpioClient, gpio_port: GPIOPort):
        """
        Inicializar el handler con las implementaciones inyectadas.
        
        Mapeo fijo: GPIO1 → Coil 1, GPIO2 → Coil 2, ..., GPIO5 → Coil 5
        
        Args:
            modbus_client: Implementación del cliente Modbus para GPIO
            gpio_port: Implementación del puerto GPIO físico
        """
        self.modbus_client = modbus_client
        self.gpio_port = gpio_port
        
        # Mapeo fijo: GPIO1->Coil1, GPIO2->Coil2, etc.
        self._pin_mapping: Dict[int, int] = {
            1: 1,  # GPIO1 → Coil 1
            2: 2,  # GPIO2 → Coil 2  
            3: 3,  # GPIO3 → Coil 3
            4: 4,  # GPIO4 → Coil 4
        }
        
        self._is_running = False
        
        _logger.info("GPIOModbusHandler inicializado con mapeo fijo GPIO1-5 → Coil1-5")
    
    def get_supported_gpios(self) -> list[int]:
        """
        Obtener la lista de GPIOs soportados (1-5).
        
        Returns:
            list: Lista de números de GPIO soportados [1, 2, 3, 4]
        """
        return list(self._pin_mapping.keys())
    
    def get_modbus_address(self, gpio_pin: int) -> int:
        """
        Obtener la dirección Modbus para un GPIO específico.
        
        Args:
            gpio_pin: Número del GPIO (1-5)
            
        Returns:
            int: Dirección del coil Modbus correspondiente
            
        Raises:
            ValueError: Si el GPIO no está soportado
        """
        if gpio_pin not in self._pin_mapping:
            raise ValueError(f"GPIO{gpio_pin} no soportado. GPIOs válidos: {self.get_supported_gpios()}")
        
        return self._pin_mapping[gpio_pin]
   
    
    def write_gpio_via_modbus(self, gpio_pin: int, state: State) -> None:
        """
        Escribir estado a un GPIO mediante Modbus.
        
        Args:
            gpio_pin: GPIO a controlar (1-5)
            state: Estado a escribir (ON/OFF)
            
        Raises:
            ValueError: Si el GPIO no es válido (debe ser 1-5)
            Exception: Si hay error en la comunicación
        """
        if gpio_pin not in self._pin_mapping:
            raise ValueError(f"GPIO{gpio_pin} no válido. GPIOs soportados: {self.get_supported_gpios()}")
        
        modbus_address = self._pin_mapping[gpio_pin]
        modbus_value = state == State.ON
        
        _logger.debug(f"Escribiendo GPIO{gpio_pin} (Coil {modbus_address}) = {state.name}")
        
        try:
            self.modbus_client.write_coil(modbus_address, modbus_value)
            _logger.info(f"GPIO{gpio_pin} establecido a {state.name} vía Modbus")
            
        except Exception as e:
            _logger.error(f"Error escribiendo GPIO{gpio_pin} vía Modbus: {e}")
            raise
    
    def read_gpio_via_modbus(self, gpio_pin: int) -> State:
        """
        Leer estado de un GPIO mediante Modbus.
        
        Args:
            gpio_pin: GPIO a leer (1-4)
            
        Returns:
            State: Estado actual del GPIO (ON/OFF)
            
        Raises:
            ValueError: Si el GPIO no es válido (debe ser 1-5)
            Exception: Si hay error en la comunicación
        """
        if gpio_pin not in self._pin_mapping:
            raise ValueError(f"GPIO{gpio_pin} no válido. GPIOs soportados: {self.get_supported_gpios()}")
        
        modbus_address = self._pin_mapping[gpio_pin]
        
        try:
            modbus_value = self.modbus_client.read_coil(modbus_address)
            state = State.ON if modbus_value else State.OFF
            
            _logger.info(f"GPIO{gpio_pin} (Coil {modbus_address}) leído: {state.name}")
            return state
            
        except Exception as e:
            _logger.error(f"Error leyendo GPIO{gpio_pin} vía Modbus: {e}")
            raise
    
    def write_physical_gpio(self, gpio_pin: int, state: State) -> None:
        """
        Escribir estado directamente al GPIO físico.
        
        Args:
            gpio_pin: GPIO a escribir (1-5)
            state: Estado a escribir (ON/OFF)
            
        Raises:
            ValueError: Si el GPIO no es válido (debe ser 1-5)
        """
        if gpio_pin not in self._pin_mapping:
            raise ValueError(f"GPIO{gpio_pin} no válido. GPIOs soportados: {self.get_supported_gpios()}")
            
        _logger.debug(f"Escribiendo GPIO{gpio_pin} físico = {state.name}")
        
        try:
            if self.gpio_port.get_direction(gpio_pin) != GpioDirection.OUTPUT:
                _logger.warning(f"GPIO{gpio_pin} no está configurado como OUTPUT en el puerto físico.")
                return
            
            result = self.gpio_port.write(gpio_pin, state)
            if not result: 
                raise Exception("Falló la escritura en el GPIO físico")
            _logger.info(f"GPIO{gpio_pin} físico establecido a {state.name}")
            
        except Exception as e:
            _logger.error(f"Error escribiendo GPIO{gpio_pin} físico: {e}")
            raise
    
    def read_physical_gpio(self, gpio_pin: int) -> State:
        """
        Leer estado directamente del GPIO físico.
        
        Args:
            gpio_pin: GPIO a leer (1-5)
            
        Returns:
            State: Estado actual del GPIO físico
            
        Raises:
            ValueError: Si el GPIO no es válido (debe ser 1-5)
        """
        if gpio_pin not in self._pin_mapping:
            raise ValueError(f"GPIO{gpio_pin} no válido. GPIOs soportados: {self.get_supported_gpios()}")
            
        try:
            state = self.gpio_port.read(gpio_pin)
            _logger.debug(f"GPIO{gpio_pin} físico leído: {state.name}")
            return state
            
        except Exception as e:
            _logger.error(f"Error leyendo GPIO{gpio_pin} físico: {e}")
            raise
    
    def sync_physical_to_modbus(self, gpio_pin: int) -> None:
        """
        Sincronizar estado del GPIO físico hacia Modbus.
        
        Args:
            gpio_pin: GPIO a sincronizar (1-5)
        """
        try:
            # Leer estado físico
            physical_state = self.read_physical_gpio(gpio_pin)
            
            # Escribir a Modbus
            self.write_gpio_via_modbus(gpio_pin, physical_state)
            
            _logger.info(f"Sincronizado GPIO{gpio_pin}: físico → Modbus ({physical_state.name})")
            
        except Exception as e:
            _logger.error(f"Error sincronizando GPIO{gpio_pin} físico → Modbus: {e}")
            raise
    
    def sync_modbus_to_physical(self, gpio_pin: int) -> None:
        """
        Sincronizar estado de Modbus hacia el GPIO físico.
        
        Args:
            gpio_pin: GPIO a sincronizar (1-5)
        """
        try:
            # Leer estado Modbus
            modbus_state = self.read_gpio_via_modbus(gpio_pin)
            
            # Escribir al GPIO físico
            self.write_physical_gpio(gpio_pin, modbus_state)
            
            _logger.info(f"Sincronizado GPIO{gpio_pin}: Modbus → físico ({modbus_state.name})")
            
        except Exception as e:
            _logger.error(f"Error sincronizando GPIO{gpio_pin} Modbus → físico: {e}")
            raise
    
    def sync_all_physical_to_modbus(self) -> None:
        """Sincronizar todos los GPIOs (1-5) del físico hacia Modbus."""
        _logger.info("Sincronizando todos los GPIOs (1-5): físico → Modbus")
        
        for gpio_pin in self._pin_mapping.keys():
            try:
                self.sync_physical_to_modbus(gpio_pin)
            except Exception as e:
                _logger.error(f"Error sincronizando GPIO{gpio_pin}: {e}")
                # Continuar con el siguiente pin
    
    def sync_all_modbus_to_physical(self) -> None:
        """Sincronizar todos los GPIOs (1-5) de Modbus hacia el físico."""
        _logger.info("Sincronizando todos los GPIOs (1-5): Modbus → físico")
        
        for gpio_pin in self._pin_mapping.keys():
            try:
                self.sync_modbus_to_physical(gpio_pin)
            except Exception as e:
                _logger.error(f"Error sincronizando GPIO{gpio_pin}: {e}")
                # Continuar con el siguiente pin
    
     




class GPIOSyncService:
    """Servicio para sincronizar periódicamente GPIO físico y Modbus."""
    
    def __init__(self, handler: GPIOModbusHandler, interval: int = 5):
        """
        Inicializar el servicio de sincronización.
        
        Args:
            handler: Instancia del GPIOModbusHandler
            interval: Intervalo de sincronización en segundos
        """
        self.handler = handler
        self.interval = interval
        self._is_running = False
    
    def start(self) -> None:
        """Iniciar el servicio de sincronización."""
        self._is_running = True
        _logger.info("Servicio de sincronización GPIO-Modbus iniciado.")
        
        while self._is_running:
            try:
                self.handler.sync_all_modbus_to_physical()
                self.handler.sync_all_physical_to_modbus()
            except Exception as e:
                _logger.error(f"Error en la sincronización periódica: {e}")
            finally: 
                time.sleep(self.interval)
    
    def stop(self) -> None:
        """Detener el servicio de sincronización."""
        self._is_running = False
        _logger.info("Servicio de sincronización GPIO-Modbus detenido.")