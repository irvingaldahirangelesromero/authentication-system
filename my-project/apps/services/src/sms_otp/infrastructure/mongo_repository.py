# Ruta: authentication/my-project/apps/services/src/sms_otp/infrastructure/mongo_repository.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDBUserRepository:
    def __init__(self):
        # CONEXIÓN CORRECTA A MONGODB ATLAS
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb+srv://autentication:gashj421b@cluster0.xoe7f.mongodb.net/autentication?retryWrites=true&w=majority&appName=Cluster0')
        database_name = os.getenv('MONGODB_DB_NAME', 'autentication')
        
        print(f"🔗 Conectando a MongoDB Atlas...")
        try:
            self.client = MongoClient(mongo_uri)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[database_name]
            self.collection = self.db['users']
            print(f"✅ Conectado a MongoDB Atlas: {database_name}.users")
            
            # Verificar que podemos hacer operaciones
            count = self.collection.count_documents({})
            print(f"📊 Total de usuarios en BD: {count}")
            
        except Exception as e:
            print(f"❌ ERROR conectando a MongoDB Atlas: {e}")
            raise

    def save_user(self, email, user_data):
        """Guarda o actualiza un usuario"""
        try:
            result = self.collection.update_one(
                {'email': email},
                {'$set': user_data},
                upsert=True
            )
            print(f"💾 Usuario guardado/actualizado en MongoDB Atlas: {email}")
            return result.upserted_id or result.modified_count > 0
        except Exception as e:
            print(f"❌ Error guardando usuario en MongoDB: {e}")
            return False

    def get_user(self, email):
        """Obtiene un usuario por email"""
        try:
            user = self.collection.find_one({'email': email})
            if user:
                print(f"🔍 Usuario encontrado en MongoDB Atlas: {email}")
            else:
                print(f"🔍 Usuario NO encontrado en MongoDB Atlas: {email}")
            return user
        except Exception as e:
            print(f"❌ Error buscando usuario en MongoDB: {e}")
            return None

    def update_user(self, email, updates):
        """Actualiza un usuario"""
        try:
            result = self.collection.update_one(
                {'email': email},
                {'$set': updates}
            )
            success = result.modified_count > 0
            if success:
                print(f"✏️ Usuario actualizado en MongoDB Atlas: {email}")
            return success
        except Exception as e:
            print(f"❌ Error actualizando usuario en MongoDB: {e}")
            return False

    def user_exists(self, email):
        """Verifica si un usuario existe"""
        try:
            exists = self.collection.count_documents({'email': email}) > 0
            print(f"🔎 Usuario existe en MongoDB Atlas {email}: {exists}")
            return exists
        except Exception as e:
            print(f"❌ Error verificando usuario en MongoDB: {e}")
            return False