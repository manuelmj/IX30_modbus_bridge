from enum import Enum


class ServiceType(Enum):
    MODBUS_SERVER = "modbus_server"
    GPIO_MODBUS_CLIENT = "gpio_modbus_client"
    GPIO_PORT = "gpio_port"
    ANALOG_MODBUS_CLIENT = "analog_modbus_client"
    ANALOG_PORT = "analog_port"

    GPIO_SYNC_SERVICE = "gpio_sync_service"
    ANALOG_SYNC_SERVICE = "analog_sync_service"
    

class GpioDirection(Enum):
    INPUT = "input"
    OUTPUT = "output"

class State(Enum):
    OFF = 0
    ON = 1
 
 

