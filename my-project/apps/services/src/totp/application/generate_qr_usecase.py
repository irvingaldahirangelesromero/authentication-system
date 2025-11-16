# Ruta: authentication/my-project/apps/services/src/totp/application/generate_qr_usecase.py
from domain.otp_generator import OTPGenerator  # AÑADE ESTA IMPORTACIÓN

class GenerateQRUseCase:
    def __init__(self, qr_service):
        self.qr_service = qr_service

    def execute(self, secret, email, issuer):
        otp = OTPGenerator(secret=secret)
        uri = otp.generate_uri(usr_email=email, issuer_name=issuer)
        return self.qr_service.generate_qr_image(uri)