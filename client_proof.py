from pymodbus.client import ModbusTcpClient
import time
from infrastructure.utils import ModbusUtilities


def test_server_memory():
    client = ModbusTcpClient('10.0.0.65', port=5020)
    
    if client.connect():
        try:
            # 1. Leer estado inicial
            print("=== ESTADO INICIAL ===")
            result1 = client.read_coils(address=1, count=8)
            print("Coitl totales",result1.bits)
            print("Coils:", result1.bits[:4])

     
            # 2. Escribir coil 4 a False
            print("=== ESCRIBIENDO COIL 4 A False ===")
            write_result = client.write_coil(address=4, value=True)
            print("Write success:", not write_result.isError())
            
            # # 3. Leer inmediatamente después
            # print("=== LECTURA INMEDIATA ===")
            # result2 = client.read_coils(address=0, count=4)
            # print("Coils después de escribir:", result2.bits[:4])
            
            # # 4. Pequeña pausa y leer nuevamente
            # time.sleep(1)
            # print("=== LECTURA DESPUÉS DE 1s ===")
            # result3 = client.read_coils(address=0, count=4)
            # print("Coils después de 1s:", result3.bits[:4])
            
            # # Verificar si el cambio persistió
            # if result2.bits[4] == False and result3.bits[4] == False:
            #     print("✅ Cambio PERSISTE en el servidor")
            # else:
            #     print("❌ Cambio NO persiste")



            # leer holding registers
            print("=== LECTURA HOLDING REGISTERS ===")
            hr_result = client.read_holding_registers(address=40001 , count=9)
            
            print("Holding Registers:", hr_result.registers)
            for i, val in enumerate(hr_result.registers):
                print(f"Register {i+1}: {val}")

            for i in range(0, 8, 2):
                register1 = hr_result.registers[i]
                register2 = hr_result.registers[i+1]
                canal_num = (i // 2) + 1
                print(f"Canal {canal_num} - Registers {40001 + i}, {40001 + i + 1}: {register1}, {register2}")
                
                # Convertir a float
                try:
                    float_val = ModbusUtilities.registers_to_float([register1, register2])
                    print(f"  → Float: {float_val:.6f}")
                except Exception as e:
                    print(f"  → Error convirtiendo: {e}")




        except Exception as e:
            print(f"Error: {e}")
        finally:
            client.close()

if __name__ == "__main__":
    test_server_memory()        