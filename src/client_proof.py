from pymodbus.client import ModbusTcpClient
import time
import sys
from infrastructure.utils import ModbusUtilities


def test_server_memory(ip_address='10.0.0.65', port=5020):
    client = ModbusTcpClient(ip_address, port=port)
    
    if client.connect():
        try:
            # 1. Leer estado inicial
            print("=== ESTADO INICIAL ===")
            result1 = client.read_coils(address=1, count=8)
            print("Coil totales", result1.bits)
            print("Coils:", result1.bits[:4])

            # 2. Escribir coil 4 a False
            print("=== ESCRIBIENDO COIL 4 A False ===")
            write_result = client.write_coil(address=4, value=True)
            print("Write success:", not write_result.isError())
            
            # Leer holding registers
            print("=== LECTURA HOLDING REGISTERS ===")
            hr_result = client.read_holding_registers(address=40001, count=9)
            
            print("Holding Registers:", hr_result.registers)
            for i, val in enumerate(hr_result.registers):
                print(f"Register {i+1}: {val}")

            
            print("=== CONVERSIÓN A FLOAT32 ===")
            modbus_utils = ModbusUtilities()
            for i in range(0, 8, 2):
                register1 = hr_result.registers[i]
                register2 = hr_result.registers[i+1]
                canal_num = (i // 2) + 1
                print(f"Canal {canal_num} - Registers {40001 + i}, {40001 + i + 1}: {register1}, {register2}")
                
                # Convertir a float
                try:
                    float_val = modbus_utils.convert_registers_to_float(registers=[register1, register2])
                    print(f"  → Float: {float_val:.6f}")
                except Exception as e:
                    print(f"  → Error convirtiendo: {e}")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            client.close()
    else:
        print(f"❌ No se pudo conectar al servidor Modbus en {ip_address}:{port}")


if __name__ == "__main__":
    # Usar IP por argumento o default
    ip_address = sys.argv[1] if len(sys.argv) > 1 else '10.0.0.65'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5020
    
    print(f"🔌 Conectando a {ip_address}:{port}")
    test_server_memory(ip_address, port)