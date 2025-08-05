import psycopg2
import json

def test_connection():
    try:
        # Cargar configuración
        with open('config.json', 'r') as f:
            config = json.load(f)
            db_config = config['database']
        
        print("Configuración cargada:")
        print(f"Host: {db_config['host']}")
        print(f"Database: {db_config['database']}")
        print(f"User: {db_config['user']}")
        print(f"Port: {db_config['port']}")
        print("Password: [OCULTA]")
        print()
        
        print("Intentando conectar...")
        conn = psycopg2.connect(**db_config)
        print("✅ Conexión exitosa!")
        
        # Probar una consulta simple
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"Versión de PostgreSQL: {version[0]}")
        
        # Verificar que existe la base de datos abarrotes
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()
        print(f"Base de datos actual: {current_db[0]}")
        
        # Verificar tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"Tablas encontradas: {[table[0] for table in tables]}")
        
        conn.close()
        print("✅ Prueba de conexión completada exitosamente!")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión: {e}")
        print("\nPosibles soluciones:")
        print("1. Verificar que PostgreSQL esté ejecutándose")
        print("2. Verificar host, puerto, usuario y contraseña")
        print("3. Verificar que la base de datos 'abarrotes' exista")
        print("4. Verificar permisos del usuario")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_connection()