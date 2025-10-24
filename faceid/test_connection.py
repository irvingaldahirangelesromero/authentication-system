import mysql.connector
from mysql.connector import Error

print("="*60)
print("🔍 PROBANDO CONEXIÓN A MYSQL")
print("="*60)

#CREDENCIALES
HOST = "localhost"
PORT = 3306
USER = "root"
PASSWORD = ""  
DATABASE = "faceid"

print(f"\n📊 Configuración:")
print(f"   Host: {HOST}")
print(f"   Puerto: {PORT}")
print(f"   Usuario: {USER}")
print(f"   Base de datos: {DATABASE}")
print(f"   Contraseña: {'(vacía)' if PASSWORD == '' else '(configurada)'}")
print("\n" + "="*60)
print("🔌 Conectando...")
print("="*60)

try:
    # Intentar conectar
    connection = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    
    if connection.is_connected():
        print("\n✅ ¡CONEXIÓN EXITOSA!")
        
        cursor = connection.cursor(dictionary=True)
        
        # 1. Obtener versión de MySQL
        cursor.execute("SELECT VERSION() as version")
        version = cursor.fetchone()
        print(f"\n📊 Versión MySQL: {version['version']}")
        
        # 2. Verificar base de datos actual
        cursor.execute("SELECT DATABASE() as db")
        db = cursor.fetchone()
        print(f"🗄️  Base de datos activa: {db['db']}")
        
        # 3. Listar todas las tablas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📋 Tablas en la base de datos '{DATABASE}':")
        if tables:
            for table in tables:
                table_name = list(table.values())[0]
                print(f"   ✓ {table_name}")
        else:
            print("   (No hay tablas)")
        
        # 4. Verificar tabla 'users'
        cursor.execute("SHOW TABLES LIKE 'users'")
        user_table = cursor.fetchone()
        
        if user_table:
            print(f"\n✅ La tabla 'users' EXISTE")
            
            # Mostrar estructura de la tabla
            print("\n📋 Estructura de la tabla 'users':")
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            
            print(f"\n   {'Campo':<20} {'Tipo':<25} {'Null':<8} {'Key':<10}")
            print("   " + "-"*70)
            for col in columns:
                field = col['Field']
                type_ = col['Type']
                null = col['Null']
                key = col['Key'] if col['Key'] else ''
                print(f"   {field:<20} {type_:<25} {null:<8} {key:<10}")
            
            # Verificar columnas requeridas
            required_columns = ['id', 'email', 'password', 'first_name', 'secret']
            column_names = [col['Field'] for col in columns]
            
            print("\n🔍 Verificando columnas requeridas:")
            all_ok = True
            for req_col in required_columns:
                if req_col in column_names:
                    print(f"   ✅ {req_col}")
                else:
                    print(f"   ❌ {req_col} (FALTA)")
                    all_ok = False
            
            if all_ok:
                print("\n✅ TODAS LAS COLUMNAS REQUERIDAS ESTÁN PRESENTES")
            else:
                print("\n⚠️  FALTAN COLUMNAS - Verifica tu script SQL")
            
            # Contar usuarios
            cursor.execute("SELECT COUNT(*) as total FROM users")
            count = cursor.fetchone()['total']
            print(f"\n👥 Total de usuarios registrados: {count}")
            
            # Mostrar usuarios si existen
            if count > 0:
                print("\n📋 Últimos usuarios registrados:")
                cursor.execute("""
                    SELECT id, email, first_name, 
                           DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created 
                    FROM users 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                users = cursor.fetchall()
                for user in users:
                    print(f"   • ID: {user['id']} | {user['first_name']} | {user['email']}")
                    print(f"     Creado: {user['created']}")
            
        else:
            print(f"\n❌ La tabla 'users' NO EXISTE")
            print("\n⚠️  Necesitas ejecutar este script SQL en Navicat:")
            print("\n" + "-"*60)
            print("""
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(320) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    secret TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            print("-"*60)
        
        cursor.close()
        connection.close()
        
        print("\n" + "="*60)
        print("✨ PRUEBA DE CONEXIÓN COMPLETADA")
        print("="*60)
        
        if user_table and all_ok:
            print("\n✅ TODO ESTÁ LISTO PARA USAR EL SISTEMA FACE ID")
            print("\n📝 Configuración para archivo .env:")
            print(f"""
DB_HOST={HOST}
DB_PORT={PORT}
DB_USER={USER}
DB_PASSWORD={PASSWORD}
DB_NAME={DATABASE}
            """)
            print("✅ Puedes continuar con la instalación del backend y frontend")
        else:
            print("\n⚠️  Completa los pasos faltantes antes de continuar")
        
except Error as e:
    print(f"\n❌ ERROR AL CONECTAR:")
    print(f"   Código: {e.errno}")
    print(f"   Mensaje: {e.msg}")
    print(f"\n🔧 Posibles soluciones:")
    
    if e.errno == 1045:
        print("   • Error de autenticación - Verifica usuario y contraseña")
    elif e.errno == 2003:
        print("   • No se puede conectar al servidor - Verifica que MySQL esté corriendo")
    elif e.errno == 1049:
        print("   • Base de datos no existe - Crea la base de datos 'faceid' en Navicat")
    else:
        print(f"   • Revisa la documentación del error: {e.errno}")

except Exception as e:
    print(f"\n❌ ERROR INESPERADO:")
    print(f"   {type(e).__name__}: {str(e)}")

finally:
    print("\n" + "="*60)
    print("Presiona Enter para salir...")
    input()