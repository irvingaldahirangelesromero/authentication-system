# Ruta: authentication/my-project/apps/services/src/totp/infraestructure/mongo_user_repository.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from ports.user_repository_port import UserRepositoryPort

load_dotenv()

class MongoUserRepository(UserRepositoryPort):
    def __init__(self):
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb+srv://autentication:gashj421b@cluster0.xoe7f.mongodb.net/autentication?retryWrites=true&w=majority&appName=Cluster0')
        database_name = os.getenv('MONGODB_DB_NAME', 'autentication')
        
        print(f"🔗 TOTP - Conectando a MongoDB Atlas...")
        try:
            self.client = MongoClient(mongo_uri)
            self.client.admin.command('ping')  # Test connection
            self.db = self.client[database_name]
            self.collection = self.db["users"]
            print(f"✅ TOTP - Conectado a MongoDB Atlas: {database_name}.users")
        except Exception as e:
            print(f"❌ TOTP - ERROR conectando a MongoDB Atlas: {e}")
            raise
        
    def save_user(self, email, secret, password, first_name, auth_method="totp"):
        try:
            result = self.collection.insert_one({
                "email": email,
                "password": password,
                "first_name": first_name,
                "secret": secret,
                "auth_method": auth_method,
                "phone_number": None
            })
            print(f"💾 TOTP - Usuario guardado en MongoDB Atlas: {email}")
            return result.inserted_id
        except Exception as e:
            print(f"❌ TOTP - Error guardando usuario: {e}")
            raise
            
    def get_secret_by_email(self, email):
        try:
            user = self.collection.find_one({"email": email})
            if user:
                print(f"🔍 TOTP - Secreto encontrado para: {email}")
                return user["secret"]
            else:
                print(f"🔍 TOTP - Usuario NO encontrado: {email}")
                return None
        except Exception as e:
            print(f"❌ TOTP - Error obteniendo secreto: {e}")
            return None