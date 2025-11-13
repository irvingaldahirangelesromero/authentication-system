# Ruta: autentication/my-project/apps/services/src/faceid/application/delete_user_usecase.py
from faceid.ports.user_repository_port import FaceIDUserRepositoryPort

class DeleteUserUseCase:
    def __init__(self, user_repository: FaceIDUserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, user_id: str):
        success = self.user_repository.delete_user_by_id(user_id)
        if success:
            return {"success": True, "message": "Usuario eliminado"}
        else:
            raise ValueError("Usuario no encontrado o no se pudo eliminar")