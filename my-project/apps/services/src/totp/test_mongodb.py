# quick_test.py
from pymongo import MongoClient

def test_connection():
    print("🚀 PRUEBA RÁPIDA DE CONEXIÓN")
    
    # URI CORRECTA
    uri = "mongodb+srv://autentication:gashj421b@cluster0.xoe7f.mongodb.net/autentication?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        client = MongoClient(uri)
        
        # Test de conexión
        client.admin.command('ping')
        print("✅ Ping exitoso a MongoDB Atlas")
        
        # Verificar base de datos
        db = client['autentication']
        collections = db.list_collection_names()
        print(f"✅ Base de datos 'autentication' accesible")
        print(f"📁 Colecciones: {collections}")
        
        # Test de escritura
        test_collection = db['quick_test']
        result = test_collection.insert_one({"test": "conexión exitosa"})
        print(f"✅ Escritura exitosa - ID: {result.inserted_id}")
        
        # Limpiar
        test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test limpiado")
        
        print("\n🎉 ¡CONEXIÓN EXITOSA! Tu MongoDB Atlas está funcionando.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_connection()