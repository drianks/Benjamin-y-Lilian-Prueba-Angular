import datetime
from pymongo import MongoClient

def setup_database():
    try:
        # Conectarse a MongoDB local (puerto 27017 por defecto)
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        
        # Verificar conexión
        client.admin.command('ping')
        
        # Crear o acceder a la base de datos evaluacion_hoteles
        db = client["evaluacion_hoteles"]
        
        # Colección hoteles
        collection = db["hoteles"]
        
        # Limpiar colección previa para asegurar una demo limpia e idempotente
        collection.drop()
        
        # Definición de los 8 hoteles precargados de prueba
        hoteles_iniciales = [
            {
                "nombre": "Hotel Grand Palace",
                "categoria_estrellas": 5,
                "capacidad_habitaciones": 150,
                "fecha_inauguracion": datetime.datetime(2010, 5, 20),
                "activo": True,
                "direccion": {
                    "calle": "Av. Libertador Bernardo O'Higgins 1234",
                    "ciudad": "Santiago",
                    "pais": "Chile",
                    "telefono": "+56223456789"
                },
                "habitaciones": [
                    {"numero": 101, "tipo": "Simple", "precio_noche": 45000, "disponible": True},
                    {"numero": 102, "tipo": "Doble", "precio_noche": 70000, "disponible": False},
                    {"numero": 201, "tipo": "Suite", "precio_noche": 150000, "disponible": True}
                ]
            },
            {
                "nombre": "Hotel Bahía Azul",
                "categoria_estrellas": 4,
                "capacidad_habitaciones": 80,
                "fecha_inauguracion": datetime.datetime(2015, 11, 12),
                "activo": True,
                "direccion": {
                    "calle": "Av. Borgoño 14500",
                    "ciudad": "Viña del Mar",
                    "pais": "Chile",
                    "telefono": "+56322987654"
                },
                "habitaciones": [
                    {"numero": 101, "tipo": "Simple", "precio_noche": 50000, "disponible": True},
                    {"numero": 102, "tipo": "Doble", "precio_noche": 85000, "disponible": True},
                    {"numero": 301, "tipo": "Suite", "precio_noche": 180000, "disponible": False}
                ]
            },
            {
                "nombre": "Hostal del Cerro",
                "categoria_estrellas": 3,
                "capacidad_habitaciones": 25,
                "fecha_inauguracion": datetime.datetime(2008, 9, 5),
                "activo": True,
                "direccion": {
                    "calle": "Calle Alegre 45",
                    "ciudad": "Valparaíso",
                    "pais": "Chile",
                    "telefono": "+56322112233"
                },
                "habitaciones": [
                    {"numero": 10, "tipo": "Simple", "precio_noche": 30000, "disponible": True},
                    {"numero": 12, "tipo": "Doble", "precio_noche": 45000, "disponible": True}
                ]
            },
            {
                "nombre": "Hotel Cumbres del Sur",
                "categoria_estrellas": 5,
                "capacidad_habitaciones": 110,
                "fecha_inauguracion": datetime.datetime(2018, 4, 1),
                "activo": True,
                "direccion": {
                    "calle": "Klenner 350",
                    "ciudad": "Puerto Varas",
                    "pais": "Chile",
                    "telefono": "+56652233445"
                },
                "habitaciones": [
                    {"numero": 101, "tipo": "Simple", "precio_noche": 95000, "disponible": True},
                    {"numero": 202, "tipo": "Doble", "precio_noche": 130000, "disponible": True},
                    {"numero": 505, "tipo": "Suite", "precio_noche": 250000, "disponible": True}
                ]
            },
            {
                "nombre": "Hotel Termas de Chillán",
                "categoria_estrellas": 5,
                "capacidad_habitaciones": 120,
                "fecha_inauguracion": datetime.datetime(2002, 7, 24),
                "activo": True,
                "direccion": {
                    "calle": "Camino Termas de Chillán km 80",
                    "ciudad": "Chillán",
                    "pais": "Chile",
                    "telefono": "+56422206100"
                },
                "habitaciones": [
                    {"numero": 105, "tipo": "Simple", "precio_noche": 110000, "disponible": False},
                    {"numero": 208, "tipo": "Doble", "precio_noche": 170000, "disponible": True},
                    {"numero": 401, "tipo": "Suite", "precio_noche": 290000, "disponible": True}
                ]
            },
            {
                "nombre": "Eco Hotel Antofagasta",
                "categoria_estrellas": 4,
                "capacidad_habitaciones": 95,
                "fecha_inauguracion": datetime.datetime(2020, 1, 15),
                "activo": True,
                "direccion": {
                    "calle": "Av. Grecia 1200",
                    "ciudad": "Antofagasta",
                    "pais": "Chile",
                    "telefono": "+56552548790"
                },
                "habitaciones": [
                    {"numero": 101, "tipo": "Simple", "precio_noche": 60000, "disponible": True},
                    {"numero": 102, "tipo": "Doble", "precio_noche": 90000, "disponible": True}
                ]
            },
            {
                "nombre": "Hotel Don Raúl",
                "categoria_estrellas": 3,
                "capacidad_habitaciones": 40,
                "fecha_inauguracion": datetime.datetime(1995, 3, 10),
                "activo": True,
                "direccion": {
                    "calle": "Caracoles 130",
                    "ciudad": "San Pedro de Atacama",
                    "pais": "Chile",
                    "telefono": "+56552851144"
                },
                "habitaciones": [
                    {"numero": 1, "tipo": "Simple", "precio_noche": 40000, "disponible": True},
                    {"numero": 2, "tipo": "Doble", "precio_noche": 60000, "disponible": True}
                ]
            },
            {
                "nombre": "Hotel Costa Real",
                "categoria_estrellas": 4,
                "capacidad_habitaciones": 60,
                "fecha_inauguracion": datetime.datetime(2005, 12, 18),
                "activo": False,
                "direccion": {
                    "calle": "Av. Francisco de Aguirre 300",
                    "ciudad": "La Serena",
                    "pais": "Chile",
                    "telefono": "+56512221010"
                },
                "habitaciones": [
                    {"numero": 101, "tipo": "Simple", "precio_noche": 55000, "disponible": False},
                    {"numero": 102, "tipo": "Doble", "precio_noche": 80000, "disponible": False}
                ]
            }
        ]
        
        print("--- CONFIGURACIÓN E INICIALIZACIÓN DE LA BASE DE DATOS ---")
        
        # Requisito de Rúbrica: Usar insertOne e insertMany y mostrar confirmación de resultado.
        
        # 1. Insertar el primer hotel usando insert_one 
        primer_hotel = hoteles_iniciales[0]
        res_one = collection.insert_one(primer_hotel)
        print(f"\n[OK] Método insertOne utilizado para insertar el primer hotel:")
        print(f"     Nombre: {primer_hotel['nombre']}")
        print(f"     ID generado: {res_one.inserted_id}")
        
        # 2. Insertar los otros 7 hoteles usando insert_many 
        otros_hoteles = hoteles_iniciales[1:]
        res_many = collection.insert_many(otros_hoteles)
        print(f"\n[OK] Método insertMany utilizado para insertar los {len(otros_hoteles)} hoteles restantes:")
        for idx, insert_id in enumerate(res_many.inserted_ids):
            print(f"     - Hotel '{otros_hoteles[idx]['nombre']}' insertado con ID: {insert_id}")
            
        print("\n========================================================")
        print(f"Precarga finalizada con éxito.")
        print(f"Total de documentos en la colección 'hoteles': {collection.count_documents({})}")
        print("========================================================\n")
        
        client.close()
        return True
    except Exception as e:
        print(f"\n[ERROR] No se pudo conectar a MongoDB. Asegúrate de tener el servicio activo.")
        print(f"Detalle del error: {e}\n")
        return False

if __name__ == "__main__":
    setup_database()
