from digidevice import dio
from digidevice.dio import Name, Direction as DigiDir, State as DigiState
from domain.models import State, GpioDirection
from domain.ports import GPIOPort
from infrastructure.dto_models import StateDTO, DirectionDTO, GpioMap

class DigiGPIOAdapter(GPIOPort):
    """Adaptador físico GPIO para Digi IX30"""

    def read(self, pin: int) -> State:
        gpio = GpioMap.get_gpio_name(pin)
        dir = dio.get_direction(gpio)

        if dir == DigiDir.input:
            val = dio.get_input(gpio)
        else:
            val = dio.get_output(gpio)

        return StateDTO.digi_to_domain_state_pull_up(val)
    
    def write(self, pin: int, value: State) -> bool:
        gpio = GpioMap.get_gpio_name(pin)
        dir = dio.get_direction(gpio)
        
        if dir != DigiDir.output:
            return False
        
        state = StateDTO.domain_to_digi_state_pull_up(value)
        dio.set_state(gpio, state)
        return True
        


    def get_direction(self, pin: int) -> GpioDirection:
        gpio = GpioMap.get_gpio_name(pin)
        dir = dio.get_direction(gpio)
        return DirectionDTO.digi_to_domain_direction(dir)
        
