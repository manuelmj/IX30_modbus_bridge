
import threading
import logging
import time
from typing import List
# from concurrent.futures import ThreadPoolExecutor

# Solo importar interfaces y servicios de aplicación
from domain.ports import ModbusServerPort
from application.gpio_modbus_handler import GPIOSyncService
from application.analog_modbus_handler import AnalogSyncService

_logger = logging.getLogger(__name__)

class ApplicationRunner:
    """
    RUNNER - Se encarga de EJECUTAR servicios ya ensamblados.
    
    Esta clase es la evolución de tu services.py original,
    pero recibe dependencias ya creadas en lugar de crearlas.
    """
    
    def __init__(self, 
                 modbus_server: ModbusServerPort,
                 gpio_sync_service: GPIOSyncService,
                 analog_sync_service: AnalogSyncService):
        """
        Constructor con dependencias ya ensambladas.
        
        Nota: Recibe objetos YA CREADOS, no los crea.
        """
        self.modbus_server = modbus_server
        self.gpio_sync_service = gpio_sync_service
        self.analog_sync_service = analog_sync_service
        
        self._threads: List[threading.Thread] = []
        self._running = False
    
    def start_all_services(self):
        """
        Iniciar todos los servicios en hilos separados.
        
        Esto es equivalente a llamar tus 3 funciones start_*
        pero con dependencias ya inyectadas.
        """
        if self._running:
            _logger.warning("Servicios ya están ejecutándose")
            return
        
        _logger.info("=== Iniciando todos los servicios ===")
        
        try:
            # 1. Iniciar servidor Modbus
            server_thread = self._start_modbus_server()
            
            # 2. Iniciar cliente GPIO
            gpio_thread = self._start_gpio_client()
            
            # 3. Iniciar cliente analógico
            analog_thread = self._start_analog_client()
            
            self._threads = [server_thread, gpio_thread, analog_thread]
            self._running = True
            
            _logger.info("=== Todos los servicios iniciados ===")
            
        except Exception as e:
            _logger.error(f"Error iniciando servicios: {e}")
            self.stop_all_services()
            raise
    
    def _start_modbus_server(self) -> threading.Thread:
        """
        Iniciar servidor Modbus en hilo separado.
        
        Equivalente a tu start_modbus_server() original.
        """
        thread = threading.Thread(
            target=self.modbus_server.start,
            daemon=False,
            name="ModbusServerThread"
        )
        thread.start()
        _logger.info("Servidor Modbus iniciado en hilo separado")
        return thread
    
    def _start_gpio_client(self) -> threading.Thread:
        """
        Iniciar cliente GPIO en hilo separado.
        
        Equivalente a tu start_gpio_modbus_client() original,
        pero usando dependencia ya inyectada.
        """
        thread = threading.Thread(
            target=self.gpio_sync_service.start,
            daemon=False,
            name="GPIOSyncThread"
        )
        thread.start()
        _logger.info("Servicio GPIO sync iniciado en hilo separado")
        return thread
    
    def _start_analog_client(self) -> threading.Thread:
        """
        Iniciar cliente analógico en hilo separado.
        
        Equivalente a tu start_register_modbus_client() original,
        pero usando dependencia ya inyectada.
        """
        thread = threading.Thread(
            target=self.analog_sync_service.start,
            daemon=False,
            name="AnalogSyncThread"
        )
        thread.start()
        _logger.info("Servicio Analog sync iniciado en hilo separado")
        return thread
    
    def stop_all_services(self):
        """Detener todos los servicios."""
        if not self._running:
            return
        
        _logger.info("=== Deteniendo servicios ===")
        
        # Detener servicios
        try:
            self.gpio_sync_service.stop()
        except Exception as e:
            _logger.error(f"Error deteniendo GPIO service: {e}")
        
        try:
            self.analog_sync_service.stop()
        except Exception as e:
            _logger.error(f"Error deteniendo Analog service: {e}")
        
        try:
            self.modbus_server.stop()
        except Exception as e:
            _logger.error(f"Error deteniendo Modbus server: {e}")
        
        # Esperar hilos
        for thread in self._threads:
            if thread.is_alive():
                thread.join(timeout=2.0)
        
        self._running = False
        _logger.info("=== Servicios detenidos ===")
    
    def is_running(self) -> bool:
        """Verificar si los servicios están ejecutándose."""
        return self._running
    
    def wait_for_completion(self):
        """Esperar a que todos los hilos terminen."""
        for thread in self._threads:
            thread.join()
    
    # Context manager support
    def __enter__(self):
        self.start_all_services()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_all_services()

