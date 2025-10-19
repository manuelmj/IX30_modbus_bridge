from enum import Enum
from typing import List, Optional
from domain.models import GpioDirection, State
from digidevice.dio import Name, Direction as DigiDir, State as DigiState


class GpioMap:
    GPIO_MAP = {
    1: Name.dio1,
    2: Name.dio2,
    3: Name.dio3,
    4: Name.dio4,
    }

    @staticmethod
    def get_gpio_name(pin: int) -> Name:
        if pin not in GpioMap.GPIO_MAP:
            raise ValueError(f"Pin GPIO {pin} no válido. Debe ser 1-4")
        return GpioMap.GPIO_MAP[pin]


class DirectionDTO:
    @staticmethod
    def digi_to_domain_direction(digi_dir: DigiDir) -> GpioDirection:
        """Convertir Dirección: Infra (Digi) → Dominio"""
        return GpioDirection.INPUT if digi_dir == DigiDir.input else GpioDirection.OUTPUT




# DTO para State
class StateDTO():
    @staticmethod
    def digi_to_domain_state_pull_up(digi_state: DigiState) -> State:
        """Convertir Estado: Infra (Digi) → Dominio"""
        return State.ON if digi_state == DigiState.off else State.OFF
     #  return State.OFF if val == DigiState.on else State.ON
    

    @staticmethod
    def digi_to_domain_state_pull_down(digi_state: DigiState) -> State:
        """Convertir Estado: Infra (Digi) → Dominio"""
        return State.OFF if digi_state == DigiState.on else State.ON


    @staticmethod
    def domain_to_digi_state_pull_up(domain_state: State) -> DigiState:
        """Convertir Estado: Dominio → Infra (Digi)"""
        return DigiState.off if domain_state == State.ON else DigiState.on