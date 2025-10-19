"""
MAIN - Punto de entrada que conecta Composition Root con Application Runner.

Este main:
✅ Usa Composition Root para ensamblar
✅ Usa Application Runner para ejecutar
✅ Maneja configuración de alto nivel
❌ NO conoce implementaciones concretas
"""
import logging
import signal
import sys
import time

from composition.composer import ServiceComposer
from composition.config import ServiceConfig
from composition.runner import ApplicationRunner
from domain.models import ServiceType

def setup_logging():
    """Configurar logging básico."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def setup_signal_handling(runner: ApplicationRunner):
    """Configurar manejo de señales."""
    def signal_handler(signum, frame):
        logging.info(f"Señal {signum} recibida. Cerrando...")
        runner.stop_all_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """
    Main que conecta Composition Root con Application Runner.
    
    Esto reemplaza tu main() original pero con responsabilidades separadas:
    1. ServiceComposer ensambla dependencias
    2. ApplicationRunner ejecuta servicios
    """
    setup_logging()
    _logger = logging.getLogger(__name__)
    
    config = ServiceConfig(
        server_ip="0.0.0.0",
        server_port=5020,
        client_ip="127.0.0.1",
        client_port=5020
    )
    
    composer = ServiceComposer(config)
    
    try:
        services = composer.create_complete_application()
        
        runner = ApplicationRunner(
            modbus_server=services[ServiceType.MODBUS_SERVER],
            gpio_sync_service=services[ServiceType.GPIO_SYNC_SERVICE],
            analog_sync_service=services[ServiceType.ANALOG_SYNC_SERVICE]
        )
        
        setup_signal_handling(runner)
        
        _logger.info("Iniciando IX30 Modbus Bridge...")
        
        with runner:
            _logger.info("Aplicación ejecutándose. Presiona Ctrl+C para detener.")
            
            while runner.is_running():
                time.sleep(1)
        
        _logger.info("Aplicación cerrada correctamente")
        return 0
        
    except Exception as e:
        _logger.error(f"Error en aplicación: {e}")
        return 1
    finally:
        composer.cleanup()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)