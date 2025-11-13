# Ruta: autentication/my-project/apps/services/src/faceid/application/login_password_usecase.py
from faceid.ports.user_repository_port import FaceIDUserRepositoryPort
from typing import Dict, Any

class LoginPasswordUseCase:
    def __init__(self, user_repository: FaceIDUserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, email: str, password: str) -> Dict[str, Any]:
        if not email or not password:
            raise ValueError("Email y contraseña requeridos")
            
        user = self.user_repository.get_user_by_email_and_password(email, password)
        
        if user:
            return {
                "success": True,
                "message": f"Bienvenido {user['first_name']}",
                "user": {
                    "id": str(user['_id']),
                    "email": user['email'],
                    "first_name": user['first_name']
                }
            }
        else:
            raise ValueError("Email o contraseña incorrectos")