# Ruta: autentication/my-project/apps/services/src/faceid/infraestructure/mongo_faceid_repository.py
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Dict, Any, Optional
import hashlib
import os

# Importamos el puerto para asegurarnos de que la implementación coincide
from faceid.ports.user_repository_port import FaceIDUserRepositoryPort

class MongoFaceIDRepository(FaceIDUserRepositoryPort):
    
    def __init__(self):
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb+srv://autentication:gashj421b@cluster0.xoe7f.mongodb.net/autentication?retryWrites=true&w=majority&appName=Cluster0')
        database_name = os.getenv('MONGODB_DB_NAME', 'autentication')
        
        print(f"🔗 FaceID - Conectando a MongoDB Atlas...")
        try:
            self.client = MongoClient(mongo_uri)
            self.client.admin.command('ping')
            self.db = self.client[database_name]
            self.collection = self.db["users"]
            print(f"✅ FaceID - Conectado a MongoDB Atlas: {database_name}.users")
        except Exception as e:
            print(f"❌ FaceID - ERROR conectando a MongoDB Atlas: {e}")
            raise

    def _hash_password(self, password: str) -> str:
        """Hashea una contraseña con SHA256 (igual que en tu app.py)"""
        return hashlib.sha256(password.encode()).hexdigest()

    def save_user_with_encoding(self, email: str, password: str, first_name: str, encoding_data: str) -> bool:
        """
        Usa update_one con upsert=True.
        Esto crea el usuario si no existe, o actualiza su encoding facial si ya existe.
        """
        password_hash = self._hash_password(password)
        try:
            result = self.collection.update_one(
                {"email": email},
                {"$set": {
                    "email": email,
                    "password": password_hash,
                    "first_name": first_name,
                    "face_encoding": encoding_data, # Nuevo campo para el rostro
                    "auth_method": "faceid" # O puedes tener "totp,faceid"
                }},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            print(f"Error al guardar usuario: {e}")
            return False

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"email": email})

    def get_user_by_email_and_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        password_hash = self._hash_password(password)
        return self.collection.find_one({"email": email, "password": password_hash})

    def get_all_users_with_encodings(self) -> List[Dict[str, Any]]:
        """Obtiene solo usuarios que tienen un encoding facial"""
        query = {"face_encoding": {"$ne": None, "$exists": True}}
        projection = {"_id": 1, "email": 1, "first_name": 1, "face_encoding": 1}
        return list(self.collection.find(query, projection))

    def list_all_users(self) -> List[Dict[str, Any]]:
        """Lista usuarios para el frontend, sin datos sensibles"""
        projection = {"_id": 1, "email": 1, "first_name": 1, "created_at": 1} 
        # Asumiendo que guardas 'created_at'. Si no, quítalo.
        return list(self.collection.find({}, projection).sort("first_name", 1))

    def delete_user_by_id(self, user_id: str) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar usuario (ID: {user_id}): {e}")
            return False