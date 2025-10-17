from ..domain.sms_otp_generator import SMSOTPGenerator
from ..ports.sms_service_port import SMSServicePort

class SendOTPUseCase:
    def __init__(self, sms_service: SMSServicePort):
        self.sms_service = sms_service
        self.otp_generator = SMSOTPGenerator()

    def execute(self, phone_number: str) -> bool:
        otp = self.otp_generator.generate_otp()
        return self.sms_service.send_otp(phone_number, otp)

class VerifyOTPUseCase:
    def __init__(self):
        self.otp_generator = SMSOTPGenerator()

    def execute(self, otp: str) -> bool:
        return self.otp_generator.verify_otp(otp)