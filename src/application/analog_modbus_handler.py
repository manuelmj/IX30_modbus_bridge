from domain.ports import ModbusRegisterClient, AnalogPort, ModbusOperations
from typing import Dict, List, Tuple, Deque
from collections import deque
import logging
import threading
import time

_logger = logging.getLogger(__name__)

class AnalogModbusHandler:
    """
    Manejador que integra puertos analógicos físicos con registros Modbus.
    
    Usa dos holding registers por canal para representar valores float de 32 bits.
    """
    
    def __init__(self, modbus_client: ModbusRegisterClient, 
                 analog_port: AnalogPort, 
                 modbus_operations: ModbusOperations):
        """
        Inicializar el handler con las implementaciones inyectadas.
        
        Mapeo: Cada canal analógico usa 2 holding registers (32 bits float)
        
        Args:
            modbus_client: Implementación del cliente Modbus para registros
            analog_port: Implementación del puerto analógico físico
            modbus_operations: Utilidades para conversión Modbus <-> float32
        """
        self.modbus_client = modbus_client
        self.analog_port = analog_port
        self.modbus_operations = modbus_operations

        # Canales con lectura directa vs. muestreo en background
        self.DIRECT_CHANNELS = {1, 2}
        self.SAMPLED_CHANNELS = {3, 4}
        self.MIN_SAMPLES = 100          # muestras mínimas en 1 segundo
        self.SAMPLE_WINDOW = 1.0        # ventana de tiempo en segundos
        self.SAMPLE_INTERVAL = self.SAMPLE_WINDOW / self.MIN_SAMPLES  # tiempo de espera entre muestras (s)

        # Buffers de muestreo para canales 3 y 4: deque de (timestamp, valor)
        self._sample_buffers: Dict[int, Deque[Tuple[float, float]]] = {
            ch: deque() for ch in self.SAMPLED_CHANNELS
        }
        self._sample_locks: Dict[int, threading.Lock] = {
            ch: threading.Lock() for ch in self.SAMPLED_CHANNELS
        }
        self._sampling_active = False
        self._sampling_thread: threading.Thread | None = None

        # Mapeo: Canal Analógico -> Dirección base del primer register (2 registers por canal)
        self._analog_mapping: Dict[int, int] = {
            1: 40001,  # Canal 1 → Holding Registers 40001-40002 (float32)
            2: 40003,  # Canal 2 → Holding Registers 40003-40004 (float32)
            3: 40005,  # Canal 3 → Holding Registers 40005-40006 (float32)
            4: 40007,  # Canal 4 → Holding Registers 40007-40008 (float32)
        }
        
        self._is_running = False

        _logger.info("AnalogModbusHandler inicializado - 2 registros por canal para float32")
        _logger.info(f"Canales directos: {self.DIRECT_CHANNELS} | Canales muestreados: {self.SAMPLED_CHANNELS} (min {self.MIN_SAMPLES} muestras/s, intervalo {self.SAMPLE_INTERVAL*1000:.2f} ms)")

    # ------------------------------------------------------------------ #
    #  Muestreo en background para canales 3 y 4                           #
    # ------------------------------------------------------------------ #

    def start_sampling(self) -> None:
        """Arrancar el hilo de muestreo continuo para los canales muestreados."""
        if self._sampling_active:
            return
        self._sampling_active = True
        self._sampling_thread = threading.Thread(
            target=self._sampling_loop,
            daemon=True,
            name="AnalogSamplingThread"
        )
        self._sampling_thread.start()
        _logger.info("Hilo de muestreo analógico iniciado para canales %s", self.SAMPLED_CHANNELS)

    def stop_sampling(self) -> None:
        """Detener el hilo de muestreo."""
        self._sampling_active = False
        if self._sampling_thread and self._sampling_thread.is_alive():
            self._sampling_thread.join(timeout=2)
        _logger.info("Hilo de muestreo analógico detenido")

    def _sampling_loop(self) -> None:
        """Bucle de muestreo: lee canales 3 y 4 lo más rápido posible y mantiene
        una ventana deslizante de 1 segundo en cada buffer."""
        while self._sampling_active:
            now = time.monotonic()
            cutoff = now - self.SAMPLE_WINDOW
            for ch in self.SAMPLED_CHANNELS:
                try:
                    value = self.analog_port.read_analog(ch)
                    with self._sample_locks[ch]:
                        self._sample_buffers[ch].append((now, value))
                        # Descartar muestras fuera de la ventana
                        while self._sample_buffers[ch] and self._sample_buffers[ch][0][0] < cutoff:
                            self._sample_buffers[ch].popleft()
                except Exception as e:
                    _logger.debug("Error muestreando canal %s en background: %s", ch, e)
            time.sleep(self.SAMPLE_INTERVAL)

    
    def get_modbus_addresses(self, analog_channel: int) -> Tuple[int, int]:
        """
        Obtener las direcciones Modbus para un canal analógico específico.
        
        Args:
            analog_channel: Número del canal analógico (1-4)
            
        Returns:
            Tuple[int, int]: Direcciones del primer y segundo register
            
        Raises:
            ValueError: Si el canal no está soportado
        """
        if analog_channel not in self._analog_mapping:
            raise ValueError(f"Canal analógico {analog_channel} no soportado. Canales válidos: {self.get_supported_analog_channels()}")
        
        base_address = self._analog_mapping[analog_channel]
        return base_address, base_address + 1
    
    def     _float_to_registers(self, value: float) -> List[int]:
        """
        Convertir float de 32 bits a dos registros de 16 bits.
        
        Args:
            value: Valor float a convertir
            
        Returns:
            List[int]: Lista con dos registros [high_word, low_word]
        """
        return self.modbus_operations.convert_float_to_registers(value)
    
    
    def write_analog_via_modbus(self, analog_channel: int, value: float) -> None:
        """
        Escribir valor analógico mediante Modbus (float de 32 bits).
        
        Args:
            analog_channel: Canal analógico a escribir (1-4)
            value: Valor a escribir como float32
            
        Raises:
            ValueError: Si el canal no es válido
            Exception: Si hay error en la comunicación
        """
        if analog_channel not in self._analog_mapping:
            raise ValueError(f"Canal analógico {analog_channel} no válido. Canales soportados: {self.get_supported_analog_channels()}")
        
        base_address, second_address = self.get_modbus_addresses(analog_channel)
        
        # Convertir float a dos registros
        register_values = self._float_to_registers(value)
        _logger.debug(f"Convertido {value:.6f} a registros Modbus: {register_values}")
        _logger.debug(f"Escribiendo canal {analog_channel} (Registers {base_address}-{second_address}) = {value:.6f} → {register_values}")
        
        try:
            success = self.modbus_client.write_holding_registers_process(base_address, register_values)
            if not success:
                raise Exception("Falló la escritura en los registros Modbus {success}")
            
            _logger.info(f"Canal {analog_channel} establecido a {value:.6f} vía Modbus (registers: {register_values})")

        except Exception as e:
            _logger.error(f"Error escribiendo canal {analog_channel} vía Modbus: {e}")
            raise
    
    def read_physical_analog(self, analog_channel: int) -> float:
        """
        Leer valor del canal analógico.

        - Canales 1 y 2: lectura directa al hardware en cada llamada.
        - Canales 3 y 4: devuelve el promedio del buffer interno siempre que
          contenga al menos MIN_SAMPLES muestras tomadas en el último segundo.

        Args:
            analog_channel: Canal analógico a leer (1-4)

        Returns:
            float: Valor analógico leído

        Raises:
            ValueError: Si el canal no es válido
            RuntimeError: Si el canal muestreado no tiene suficientes muestras
        """
        if analog_channel not in self._analog_mapping:
            raise ValueError(f"Canal analógico {analog_channel} no válido. Canales soportados: {self.get_supported_analog_channels()}")

        if analog_channel in self.DIRECT_CHANNELS:
            # --- Lectura directa (canales 1 y 2) ---
            try:
                value = self.analog_port.read_analog(analog_channel)
                _logger.debug(f"Canal {analog_channel} (directo) leído: {value:.6f}")
                return value
            except Exception as e:
                _logger.error(f"Error leyendo canal {analog_channel} físico: {e}")
                raise

        # --- Lectura desde buffer muestreado (canales 3 y 4) ---
        now = time.monotonic()
        cutoff = now - self.SAMPLE_WINDOW
        with self._sample_locks[analog_channel]:
            recent = [(t, v) for t, v in self._sample_buffers[analog_channel] if t >= cutoff]

        if len(recent) < self.MIN_SAMPLES:
            raise RuntimeError(
                f"Canal {analog_channel}: muestras insuficientes "
                f"({len(recent)}/{self.MIN_SAMPLES}) en el último segundo. "
                "Asegúrese de que el hilo de muestreo esté activo."
            )

        avg = sum(v for _, v in recent) / len(recent)
        _logger.debug(
            f"Canal {analog_channel} (muestreado): promedio={avg:.6f} "
            f"sobre {len(recent)} muestras"
        )
        return avg
    
    def sync_physical_to_modbus(self, analog_channel: int) -> None:
        """
        Sincronizar valor del puerto analógico físico hacia Modbus.
        
        Args:
            analog_channel: Canal a sincronizar (1-4)
        """
        try:
            # Leer valor físico
            physical_value = self.read_physical_analog(analog_channel)
            _logger.debug(f"valor físico leído para canal {analog_channel}: {physical_value:.6f}")
            # Escribir a Modbus como float32
            self.write_analog_via_modbus(analog_channel, physical_value)
            
            _logger.info(f"Sincronizado canal {analog_channel}: físico → Modbus ({physical_value:.6f})")
            
        except Exception as e:
            _logger.error(f"Error sincronizando canal {analog_channel} físico → Modbus: {e}")
            raise
    
   
    
    def sync_all_physical_to_modbus(self) -> None:
        """Sincronizar todos los canales analógicos (1-4) del físico hacia Modbus."""
        _logger.info("Sincronizando todos los canales analógicos (1-4): físico → Modbus")
        
        for analog_channel in self._analog_mapping.keys():
            try:
                self.sync_physical_to_modbus(analog_channel)
            except Exception as e:
                _logger.error(f"Error sincronizando canal {analog_channel}: {e}")
                # Continuar con el siguiente canal
    
     



class AnalogSyncService:
    """Servicio para sincronizar periódicamente puertos analógicos y Modbus."""
    
    def __init__(self, handler: AnalogModbusHandler, interval: int = 5):
        """
        Inicializar el servicio de sincronización.
        
        Args:
            handler: Instancia del AnalogModbusHandler
            interval: Intervalo de sincronización en segundos
        """
        self.handler = handler
        self.interval = interval
        self._is_running = False
    
    def start(self) -> None:
        """Iniciar el servicio de sincronización."""
        self._is_running = True
        _logger.info(f"Servicio de sincronización Analógico-Modbus iniciado (intervalo: {self.interval}s)")

        # Arrancar muestreo en background para canales muestreados (3 y 4)
        self.handler.start_sampling()
        try:
            while self._is_running:
                try:
                    # Solo sincronizamos físico → Modbus (los analógicos son generalmente de entrada)
                    self.handler.sync_all_physical_to_modbus()

                except Exception as e:
                    _logger.error(f"Error en la sincronización periódica: {e}")
                finally:
                    time.sleep(self.interval)
        finally:
            self.handler.stop_sampling()
    
    def stop(self) -> None:
        """Detener el servicio de sincronización."""
        self._is_running = False
        _logger.info("Servicio de sincronización Analógico-Modbus detenido.")