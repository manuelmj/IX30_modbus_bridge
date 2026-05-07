# IX30 Modbus Bridge

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-green.svg)](https://alistair.cockburn.us/hexagonal-architecture/)
[![Protocol](https://img.shields.io/badge/Protocol-Modbus_TCP-orange.svg)](https://modbus.org/)

## 📋 Descripción

**IX30 Modbus Bridge** es un gateway bidireccional que sincroniza estados entre GPIO/puertos analógicos físicos y registros Modbus TCP. Implementa arquitectura hexagonal (Ports & Adapters) para máxima flexibilidad, testabilidad y mantenibilidad.

**IX30 Modbus Bridge** es una implementación específica para el **router industrial DIGI IX30**, el cual cuenta con 4 puertos digitales y 4 puertos analógicos. Esta aplicación permite exponer estos puertos a través del protocolo Modbus TCP, permitiendo la lectura y escritura de los estados de los GPIOs y los valores analógicos mediante coils y holding registers respectivamente. 

Esta integración nos permite conectar el IX30 con sistemas SCADA, PLCs u otros dispositivos compatibles con Modbus TCP, facilitando la monitorización y control remoto de los puertos digitales y analógicos del IX30.



### 🎯 Funcionalidades Principales

- **🔌 GPIO Sync**: Sincronización bidireccional entre GPIO físicos (1-4) y Coils Modbus (1-4)
- **📊 Analog Sync**: Sincronización bidireccional entre canales analógicos (1-4) y Holding Registers Modbus
- **🖥️ Modbus Server**: Expone GPIO y datos analógicos vía protocolo Modbus TCP
- **🔄 Sync Services**: Servicios de sincronización automática en tiempo real
- **⚡ Threading**: Manejo concurrente de múltiples servicios
- **🏗️ Clean Architecture**: Implementación ejemplar de patrones SOLID


## 🔄 Mapeo de Datos

### GPIO ↔ Modbus Coils
| GPIO Físico | Coil Modbus | Función |
|-------------|-------------|---------|
| GPIO 1      | Coil 1      | Digital I/O |
| GPIO 2      | Coil 2      | Digital I/O |
| GPIO 3      | Coil 3      | Digital I/O |
| GPIO 4      | Coil 4      | Digital I/O |

### Analógico ↔ Modbus Holding Registers
| Canal Analógico | Holding Registers | Tipo de Dato          | Modo de lectura              |
|-----------------|------------------|-----------------------|------------------------------|
| Canal 1         | 40001-40002      | Float32 (2 registros) | Lectura directa instantánea  |
| Canal 2         | 40003-40004      | Float32 (2 registros) | Lectura directa instantánea  |
| Canal 3         | 40005-40006      | Float32 (2 registros) | Promedio de ≥100 muestras/s  |
| Canal 4         | 40007-40008      | Float32 (2 registros) | Promedio de ≥100 muestras/s  |

#### Modos de lectura analógica

**Canales 1 y 2 — Lectura directa**  
En cada ciclo de sincronización se realiza **una única lectura** del hardware y ese valor se escribe directamente en los holding registers correspondientes.

**Canales 3 y 4 — Lectura promediada con muestreo en background**  
Un hilo dedicado (`AnalogSamplingThread`) muestrea los canales 3 y 4 de forma continua, manteniendo una **ventana deslizante de 1 segundo**. En cada ciclo de sincronización se verifica que existan al menos **100 muestras** dentro de esa ventana; si se cumple la condición, se calcula el promedio y se escribe en los registros. Si no hay suficientes muestras se registra un error y se continúa con el siguiente canal.

```
[AnalogSamplingThread - continuo]          [AnalogSyncService - cada interval s]
  Lee canal 3 y 4 lo más rápido posible      Para canal 1/2: lectura directa
  Guarda (timestamp, valor) en deque    →    Para canal 3/4: promedio del deque
  Descarta muestras > 1 s de antigüedad →    Escribe resultado en holding registers

[Cliente Modbus externo]
  Lee 40001-40002 / 40003-40004 → último valor puntual
  Lee 40005-40006 / 40007-40008 → último promedio calculado
```

> **Nota:** el intervalo de actualización de los registros está controlado por el parámetro `interval` de `AnalogSyncService` (por defecto 5 s). Reducirlo a `interval=1` actualiza los registros cada segundo con el promedio más reciente.

## 🚀 Instalación y Despliegue

### Prerrequisitos
- **Desarrollo**: Python 3.11+, Git
- **Producción**: Router DIGI IX30 con acceso SSH
- **Red**: Conectividad SSH entre PC de desarrollo y DIGI IX30

### 📋 Método 1: Despliegue Remoto (Recomendado)

#### 🌐 Paso 1: Upload al DIGI IX30
```bash
# Dar permisos de ejecución al script
chmod +x upload_compressed.sh

# Enviar proyecto completo al DIGI IX30 vía SSH
./upload_compressed.sh <usuario> <ip_digi_ix30>

# Ejemplo:
./upload_compressed.sh root 192.168.1.100
```

**¿Qué hace el script `upload_compressed.sh`?**
1. **Comprime** el directorio `src/` → `IX30_modbus_bridge.tar.gz`
2. **Copia** el script de instalación a `packages/`
3. **Envía** todo el paquete al DIGI via SCP a `/tmp/packages/`
4. **Transfiere**: Código fuente + dependencias + instalador

#### 🔧 Paso 2: Instalación en el DIGI IX30
```bash
# Conectarse al DIGI IX30 por SSH
ssh root@192.168.1.100

# Ejecutar instalación automática
cd /tmp/packages
chmod +x install_ix30_bridge.sh
./install_ix30_bridge.sh
```

**¿Qué hace el script `install_ix30_bridge.sh`?**
1. **Verifica** dependencias (pymodbus 3.11.1)
2. **Instala** pymodbus si no está presente
3. **Extrae** el código fuente a `/opt/custom/main/`
4. **Limpia** procesos anteriores si existen
5. **Inicia** el servicio automáticamente (opcional)

#### 📺 Salida Esperada de la Instalación
```bash
Instalando IX30 Modbus Bridge...
🔹 pymodbus ya está instalado en la versión 3.11.1, omitiendo instalación.
✅ IX30 Modbus Bridge instalado correctamente en /opt/custom/.
desea ejecutar el puente modbus ahora? (s/n) s
Iniciando IX30 Modbus Bridge...
✅ Puente modbus iniciado correctamente.
  PID TTY          TIME CMD
 1234 pts/0    00:00:00 python3
```

### 📋 Método 2: Instalación Manual

#### Desarrollo Local
```bash
# Clonar repositorio
git clone <repository-url>
cd ix30_modbus_bridge

# Instalar dependencias
pip install pymodbus==3.11.1

# Ejecutar desde src/
cd src
python main.py
```

### Configuración
```python
# composition/config.py
class ServiceConfig:
    server_ip: str = "0.0.0.0"     # IP del servidor Modbus (todas las interfaces)
    server_port: int = 5020        # Puerto del servidor Modbus
    client_ip: str = "127.0.0.1"   # IP del cliente Modbus (loopback)
    client_port: int = 5020        # Puerto del cliente Modbus
```

#### Personalización de la Configuración
```bash
# Editar configuración antes del despliegue
nano src/composition/config.py

# O después del despliegue en el DIGI
ssh root@192.168.1.100
nano /opt/custom/main/composition/config.py
```

## 🎮 Uso y Operación

### 🚀 Inicio del Servicio

#### En el DIGI IX30 (Producción)
```bash
# Método 1: Inicio automático (post-instalación)
# Responder 's' cuando se pregunte: "desea ejecutar el puente modbus ahora? (s/n)"

# Método 2: Inicio manual
ssh root@192.168.1.100
python3 /opt/custom/main/main.py &

```

#### En Desarrollo Local
```bash
cd src
python main.py
```

### 📊 Verificar Estado del Servicio

#### Verificar Proceso Activo
```bash
# En el DIGI IX30
ps | grep "python3 /opt/custom/main/main.py" | grep -v grep

# Verificar puerto Modbus
netstat -tlnp | grep :5020
```

#### Logs del Sistema
```bash
# Ver logs en tiempo real (desarrollo)
python3 /opt/custom/main/main.py

# Logs típicos al iniciar:
2024-10-19 10:00:00 - root - INFO - Iniciando IX30 Modbus Bridge...
2024-10-19 10:00:01 - composition.composer - INFO - Servicios ensamblados correctamente
2024-10-19 10:00:02 - application.gpio_modbus_handler - INFO - GPIOModbusHandler iniciado con mapeo GPIO1-4 → Coil1-4
2024-10-19 10:00:03 - application.analog_modbus_handler - INFO - AnalogModbusHandler iniciado - 2 registros por canal
2024-10-19 10:00:04 - infrastructure.modbus_server_adapter - INFO - Servidor Modbus iniciado en 0.0.0.0:5020
2024-10-19 10:00:05 - root - INFO - Aplicación ejecutándose. Presiona Ctrl+C para detener.
```

### 🛑 Detener el Servicio

#### Detener Proceso
```bash
# Presionar Ctrl+C para shutdown graceful
^C
2024-10-18 10:05:00 - root - INFO - Señal 2 recibida. Cerrando...
2024-10-18 10:05:01 - root - INFO - Aplicación cerrada correctamente
```

### Patrones Implementados
- ✅ **Dependency Inversion Principle (DIP)**
- ✅ **Single Responsibility Principle (SRP)**
- ✅ **Open/Closed Principle (OCP)**
- ✅ **Interface Segregation Principle (ISP)**
- ✅ **Dependency Injection Pattern**
- ✅ **Factory Pattern**
- ✅ **Adapter Pattern**
- ✅ **Composition Root Pattern**

## 📞 Contacto

- **Autor**: Manuel Manjarres Rivera
- **Email**: manuelmj1229@gmail.com




⭐ **¡Dale una estrella si este proyecto te fue útil!** ⭐