from twilio.rest import Client
from ..ports.sms_service_port import SMSServicePort
import os
from dotenv import load_dotenv

load_dotenv()

class TwilioSMSAdapter(SMSServicePort):
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_FROM_NUMBER')
        self.client = Client(self.account_sid, self.auth_token)

    def send_otp(self, phone_number: str, otp: str) -> bool:
        try:
            message = self.client.messages.create(
                body=f'Tu código de verificación es: {otp}',
                from_=self.from_number,
                to=phone_number
            )
            return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False