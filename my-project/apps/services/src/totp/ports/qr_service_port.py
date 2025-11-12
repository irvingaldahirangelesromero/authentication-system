# Ruta: authentication/my-project/apps/services/src/totp/ports/qr_service_port.py
from abc import ABC, abstractmethod

class QRServicePort(ABC):
    @abstractmethod
    def generate_qr_image(self, uri: str) -> bytes:
        pass