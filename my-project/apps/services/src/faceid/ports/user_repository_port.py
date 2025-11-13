# Ruta: autentication/my-project/apps/services/src/faceid/ports/user_repository_port.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class FaceIDUserRepositoryPort(ABC):
    
    @abstractmethod
    def save_user_with_encoding(self, email: str, password_hash: str, first_name: str, encoding_data: str) -> bool:
        """Guarda o actualiza un usuario con su encoding facial"""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca un usuario por su email"""
        pass

    @abstractmethod
    def get_user_by_email_and_password(self, email: str, password_hash: str) -> Optional[Dict[str, Any]]:
        """Busca un usuario por email y contraseña hasheada"""
        pass
        
    @abstractmethod
    def get_all_users_with_encodings(self) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios que tienen un encoding facial registrado"""
        pass
    
    @abstractmethod
    def list_all_users(self) -> List[Dict[str, Any]]:
        """Lista todos los usuarios (información pública)"""
        pass
        
    @abstractmethod
    def delete_user_by_id(self, user_id: str) -> bool:
        """Elimina un usuario por su ID"""
        pass