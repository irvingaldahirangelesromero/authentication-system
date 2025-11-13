# Ruta: autentication/my-project/apps/services/src/faceid/application/delete_user_usecase.py
from faceid.ports.user_repository_port import FaceIDUserRepositoryPort

class ListUsersUseCase:
    def __init__(self, user_repository: FaceIDUserRepositoryPort):
        self.user_repository = user_repository

    def execute(self):
        users = self.user_repository.list_all_users()
        # Convertir ObjectId a string para que sea serializable en JSON
        users_list = [
            {
                "id": str(user['_id']),
                "email": user.get('email'),
                "first_name": user.get('first_name'),
                "createdAt": user.get('created_at', '').isoformat() if user.get('created_at') else None
            } for user in users
        ]
        return {"success": True, "users": users_list}