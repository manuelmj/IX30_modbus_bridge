# IX30 Modbus Bridge

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-green.svg)](https://alistair.cockburn.us/hexagonal-architecture/)
[![Protocol](https://img.shields.io/badge/Protocol-Modbus_TCP-orange.svg)](https://modbus.org/)

## 📋 Descripción

**IX30 Modbus Bridge** es un gateway bidireccional que sincroniza estados entre GPIO/puertos analógicos físicos y registros Modbus TCP. Implementa arquitectura hexagonal (Ports & Adapters) para máxima flexibilidad, testabilidad y mantenibilidad.

Ix30 modbus bridge es una implmentacion especifica para el router industrial DIGI IX30, el cual cuenta con 4 puertos digitales y 4 puertos analogicos. Esta aplicacion permite exponer estos puertos a traves del protocolo Modbus TCP, permitiendo la lectura y escritura de los estados de los GPIOs y los valores analogicos mediante coils y holding registers respectivamente. Esta integracion nos permite conectar el IX30 con sistemas SCADA, PLCs u otros dispositivos compatibles con Modbus TCP, facilitando la monitorizacion y control remoto de los puertos digitales y analogicos del IX30.



### 🎯 Funcionalidades Principales

- **🔌 GPIO Sync**: Sincronización bidireccional entre GPIO físicos (1-4) y Coils Modbus (1-4)
- **📊 Analog Sync**: Sincronización bidireccional entre canales analógicos (1-4) y Holding Registers Modbus
- **🖥️ Modbus Server**: Expone GPIO y datos analógicos vía protocolo Modbus TCP
- **🔄 Sync Services**: Servicios de sincronización automática en tiempo real
- **⚡ Threading**: Manejo concurrente de múltiples servicios
- **🏗️ Clean Architecture**: Implementación ejemplar de patrones SOLID

## 🏛️ Arquitectura

### Arquitectura Hexagonal (Ports & Adapters)

```
┌─────────────────────────────────────────────┐
│                  MAIN.PY                    │
│            (Entry Point)                    │
└──────────────┬──────────────────────────────┘
               │
┌─────────────────────────────────────────────┐
│               COMPOSITION                   │
│   ┌─────────────┐ ┌─────────────┐          │
│   │   Config    │ │   Composer  │          │
│   └─────────────┘ └─────────────┘          │
│   ┌─────────────────────────────────────┐   │
│   │         Runner                      │   │
│   │      (Threading & Lifecycle)        │   │
│   └─────────────────────────────────────┘   │
└──────────────┬──────────────────────────────┘
               │
┌─────────────────────────────────────────────┐
│              APPLICATION                    │
│   ┌──────────────────┐ ┌─────────────────┐  │
│   │ GPIOModbusHandler│ │AnalogModbusHandler│ │
│   │    (Use Cases)   │ │   (Use Cases)    │  │
│   └──────────────────┘ └─────────────────┘  │
└──────────────┬──────────────────────────────┘
               │
┌─────────────────────────────────────────────┐
│                 DOMAIN                      │
│   ┌─────────────┐ ┌─────────────┐          │
│   │   Ports     │ │   Models    │          │
│   │ (Interfaces)│ │ (Entities)  │          │
│   └─────────────┘ └─────────────┘          │
└──────────────┬──────────────────────────────┘
               │
┌─────────────────────────────────────────────┐
│            INFRASTRUCTURE                   │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│ │GPIO Adapter │ │Modbus Client│ │Modbus   │ │
│ │   (HW)      │ │  Adapter    │ │ Server  │ │
│ └─────────────┘ └─────────────┘ └─────────┘ │
└─────────────────────────────────────────────┘
```


## 🔄 Mapeo de Datos

### GPIO ↔ Modbus Coils
| GPIO Físico | Coil Modbus | Función |
|-------------|-------------|---------|
| GPIO 1      | Coil 1      | Digital I/O |
| GPIO 2      | Coil 2      | Digital I/O |
| GPIO 3      | Coil 3      | Digital I/O |
| GPIO 4      | Coil 4      | Digital I/O |

### Analógico ↔ Modbus Holding Registers
| Canal Analógico | Holding Registers | Tipo de Dato |
|-----------------|------------------|--------------|
| Canal 1         | 40001-40002      | Float32 (2 registros) |
| Canal 2         | 40003-40004      | Float32 (2 registros) |
| Canal 3         | 40005-40006      | Float32 (2 registros) |
| Canal 4         | 40007-40008      | Float32 (2 registros) |

## 🚀 Instalación

### Prerrequisitos
- Python 3.11+
- pip o poetry

### Instalar Dependencias
```bash
# Clonar repositorio
git clone <repository-url>
cd ix30_modbus_bridge

# Instalar dependencias
pip install pymodbus
```

### Configuración
```python
# Las configuraciones se manejan en composition/config.py
class ServiceConfig:
    server_ip: str = "0.0.0.0"     # IP del servidor Modbus 
    server_port: int = 5020        # Puerto del servidor Modbus
    client_ip: str = "127.0.0.1"   # IP del servidor modbus (en este caso el local)
    client_port: int = 5020        # Puerto al que que se conecta el cliente Modbus
```

## 🎮 Uso

### Ejecución Básica
```bash
python main.py
```

### Detener la Aplicación
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