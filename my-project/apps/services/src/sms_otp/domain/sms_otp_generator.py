from django_otp.oath import TOTP
from datetime import datetime
import time

class SMSOTPGenerator:
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or self._generate_secret()
        self.step = 30
        self.digits = 6

    def _generate_secret(self) -> str:
        return TOTP.random_base32()

    def generate_otp(self) -> str:
        totp = TOTP(self.secret_key, step=self.step, digits=self.digits)
        totp.time = time.time()
        return totp.token()

    def verify_otp(self, token: str) -> bool:
        totp = TOTP(self.secret_key, step=self.step, digits=self.digits)
        totp.time = time.time()
        return totp.verify(token, tolerance=1)