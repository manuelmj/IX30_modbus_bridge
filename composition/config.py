
from dataclasses import dataclass


@dataclass
class ServiceConfig:
    """Configuración centralizada."""
    server_ip: str = "0.0.0.0"
    server_port: int = 5020
    client_ip: str = "127.0.0.1"
    client_port: int = 5020
