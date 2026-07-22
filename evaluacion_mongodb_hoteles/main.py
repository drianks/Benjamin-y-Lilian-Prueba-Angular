import datetime
import re
import sys
from bson import ObjectId
from pymongo import MongoClient

def connect_db():
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        return client, client["evaluacion_hoteles"]["hoteles"]
    except Exception as e:
        print(f"\n[ERROR] No se pudo conectar a MongoDB. Asegúrate de tener el servicio levantado.")
        print(f"Detalle: {e}")
        sys.exit(1)

def mostrar_menu():
    print("\n" + "="*50)
    print("      SISTEMA CRUD - GESTIÓN DE HOTELES RUNNING MICHAEL")
    print("="*50)
    print("1.  [C] Crear un nuevo hotel (Estructura completa)")
    print("2.  [R] Listar todos los hoteles (Con Proyección)")
    print("3.  [R] Buscar por estrellas (Comparación: $gt, $lt, $gte, $lte, $ne)")
    print("4.  [R] Buscar por expresión regular ($regex en nombre)")
    print("5.  [R] Buscar por rango de fechas (Inauguración)")
    print("6.  [R] Buscar dentro de subdocumento (Ciudad) o array (Habitaciones)")
    print("7.  [U] Actualizar un campo raíz (Nombre, Estrellas o Capacidad)")
    print("8.  [U] Actualizar subdocumento (Teléfono) o array (Habitaciones)")
    print("9.  [D] Eliminar un hotel (Con confirmación previa)")
    print("10. [A] Reporte Estadístico de Precios por Ciudad (Aggregation Pipeline)")
    print("0.  Salir del sistema")
    print("="*50)

def leer_fecha(permitir_pasado=True):
    # Expresión regular que obliga a: 2 dígitos para día, 2 para mes y 4 para año, sin letras
    patron = re.compile(r"^\d{2}-\d{2}-\d{4}$")
    while True:
        fecha_str = input("Ingrese fecha (DD-MM-AAAA): ").strip()
        
        # Validar que cumpla la estructura exacta de dígitos y guiones, descartando letras
        if not patron.match(fecha_str):
            print("[ERROR] Formato inválido o contiene letras. Use DD-MM-AAAA (ej: 30-04-2018).")
            continue
            
        try:
            # Validar que la fecha sea real en el calendario (días 1-31, meses 1-12)
            fecha_dt = datetime.datetime.strptime(fecha_str, "%d-%m-%Y")
        except ValueError:
            print("[ERROR] La fecha ingresada no existe en el calendario. Intente de nuevo.")
            continue

        # Si no se permiten fechas pasadas, validar contra el día de hoy
        if not permitir_pasado:
            hoy = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if fecha_dt < hoy:
                print(f"[ERROR] No se permiten registrar fechas anteriores a la actual (hoy es {hoy.strftime('%d-%m-%Y')}).")
                continue
                
        return fecha_dt

# 1. Crear un hotel nuevo
def crear_hotel(collection):
    print("\n--- CREAR NUEVO HOTEL ---")
    nombre = input("Nombre del hotel: ").strip()
    if not nombre:
        print("[ERROR] El nombre no puede estar vacío.")
        return

    try:
        estrellas = int(input("Categoría en estrellas (1-5): "))
        capacidad = int(input("Capacidad de habitaciones: "))
    except ValueError:
        print("[ERROR] Las estrellas y la capacidad deben ser números enteros.")
        return

    # Se solicita la fecha bloqueando el registro de fechas pasadas
    fecha_inaug = leer_fecha(permitir_pasado=False)
    activo_input = input("¿El hotel está activo actualmente? (s/n): ").strip().lower()
    activo = activo_input == 's'

    # Subdocumento obligatorio: Direccion
    print("\n--- DATOS DE DIRECCIÓN ---")
    calle = input("Calle y número: ").strip()
    ciudad = input("Ciudad: ").strip()
    pais = input("País: ").strip()
    telefono = input("Teléfono de contacto: ").strip()

    direccion = {
        "calle": calle,
        "ciudad": ciudad,
        "pais": pais,
        "telefono": telefono
    }

    # Array de subdocumentos obligatorio: Habitaciones
    habitaciones = []
    print("\n--- DATOS DE HABITACIONES ---")
    try:
        num_habs = int(input("¿Cuántas habitaciones desea ingresar inicialmente?: "))
        for i in range(num_habs):
            print(f"\nHabitación {i+1}:")
            numero = int(input("  Número de habitación: "))
            tipo = input("  Tipo (Simple / Doble / Suite): ").strip()
            precio = float(input("  Precio por noche ($): "))
            dispon = input("  ¿Está disponible? (s/n): ").strip().lower() == 's'
            
            habitaciones.append({
                "numero": numero,
                "tipo": tipo,
                "precio_noche": precio,
                "disponible": dispon
            })
    except ValueError:
        print("[ERROR] Datos de habitación inválidos. Cancelando operación.")
        return

    # Ensamblar el documento completo
    nuevo_documento = {
        "nombre": nombre,
        "categoria_estrellas": estrellas,
        "capacidad_habitaciones": capacidad,
        "fecha_inauguracion": fecha_inaug,
        "activo": activo,
        "direccion": direccion,
        "habitaciones": habitaciones
    }

    # Guardar en MongoDB
    resultado = collection.insert_one(nuevo_documento)
    print(f"\n[OK] ¡Hotel registrado exitosamente!")
    print(f"     ID de MongoDB: {resultado.inserted_id}")

# 2. Listar todos los hoteles con proyección
def listar_hoteles(collection):
    print("\n--- LISTADO COMPLETO DE HOTELES (CON PROYECCIÓN) ---")
    # Proyección de campos seleccionados para mejorar la visibilidad
    proyeccion = {
        "nombre": 1,
        "categoria_estrellas": 1,
        "direccion.ciudad": 1,
        "capacidad_habitaciones": 1,
        "activo": 1
    }
    
    hoteles = list(collection.find({}, proyeccion))
    
    if not hoteles:
        print("No se encontraron hoteles registrados.")
        return

    print(f"{'Nombre':<30} | {'Estrellas':<10} | {'Ciudad':<15} | {'Capacidad':<10} | {'Activo':<8}")
    print("-" * 80)
    for h in hoteles:
        ciudad = h.get("direccion", {}).get("ciudad", "N/A")
        activo_str = "Sí" if h.get("activo") else "No"
        print(f"{h.get('nombre', 'Sin Nombre'):<30} | {h.get('categoria_estrellas', 0):<10} | {ciudad:<15} | {h.get('capacidad_habitaciones', 0):<10} | {activo_str:<8}")

# 3. Buscar por campo simple con operador de comparación
def buscar_por_estrellas(collection):
    print("\n--- BUSCAR POR ESTRELLAS (OPERADORES DE COMPARACIÓN) ---")
    print("Seleccione el operador de comparación:")
    print("1. Mayor que ($gt)")
    print("2. Menor que ($lt)")
    print("3. Mayor o igual que ($gte)")
    print("4. Menor o igual que ($lte)")
    print("5. Distinto de ($ne)")
    
    op_choice = input("Opción (1-5): ").strip()
    operadores = {
        "1": "$gt",
        "2": "$lt",
        "3": "$gte",
        "4": "$lte",
        "5": "$ne"
    }
    
    if op_choice not in operadores:
        print("[ERROR] Selección inválida.")
        return

    op_mongo = operadores[op_choice]
    
    # Texto amigable del operador para indicarle al usuario en el segundo despliegue
    nombres_operadores = {
        "1": "MAYORES QUE (>)",
        "2": "MENORES QUE (<)",
        "3": "MAYORES O IGUALES QUE (>=)",
        "4": "MENORES O IGUALES QUE (<=)",
        "5": "DISTINTOS DE (!=)"
    }
    nombre_op = nombres_operadores[op_choice]
    
    print(f"\n--- SELECCIÓN DE ESTRELLAS DE REFERENCIA ---")
    print(f"Buscando hoteles con categoría {nombre_op} a:")
    print("5. 5 Estrellas (Excelente Calidad)")
    print("4. 4 Estrellas (Muy Buena Calidad)")
    print("3. 3 Estrellas (Buena Calidad)")
    print("2. 2 Estrellas (Calidad Estándar)")
    print("1. 1 Estrella (Calidad Básica)")
    
    valor_input = input("Seleccione estrellas (1-5): ").strip()
    if valor_input not in ["1", "2", "3", "4", "5"]:
        print("[ERROR] Selección inválida. Debe ser un número del 1 al 5.")
        return
        
    valor = int(valor_input)

    query = {"categoria_estrellas": {op_mongo: valor}}
    
    # Proyección
    proyeccion = {"nombre": 1, "categoria_estrellas": 1, "direccion.ciudad": 1}
    resultados = list(collection.find(query, proyeccion))
    
    # Mapeo descriptivo para mostrar calidad
    calidades = {
        5: "Excelente Calidad",
        4: "Muy Buena Calidad",
        3: "Buena Calidad",
        2: "Calidad Estándar",
        1: "Calidad Básica"
    }
    
    print(f"\nResultados para la consulta: categoria_estrellas {op_mongo} {valor} ({calidades[valor]})")
    print("-" * 75)
    if not resultados:
        print("No se encontraron hoteles que coincidan con la búsqueda.")
        return

    for idx, r in enumerate(resultados, 1):
        ciudad = r.get("direccion", {}).get("ciudad", "N/A")
        cat_estrellas = r.get("categoria_estrellas", 0)
        calidad_str = calidades.get(cat_estrellas, "Sin Clasificación")
        print(f"{idx}. Hotel: {r['nombre']} | Estrellas: {cat_estrellas} ({calidad_str}) | Ciudad: {ciudad}")

# 4. Buscar usando expresión regular ($regex)
def buscar_por_regex(collection):
    print("\n--- BUSCAR POR EXPRESIÓN REGULAR ($regex) ---")
    patron = input("Ingrese el texto o patrón a buscar en el nombre del hotel (o presione Enter para listar todos): ").strip()
    
    # Búsqueda insensible a mayúsculas/minúsculas usando $options: "i"
    query = {"nombre": {"$regex": patron, "$options": "i"}}
    
    # Recuperamos todos los datos de los hoteles coincidentes
    resultados = list(collection.find(query))
    
    print(f"\nResultados de búsqueda:")
    print("-" * 70)
    if not resultados:
        print("No se encontraron hoteles que coincidan con el patrón.")
        return

    # Enumerar la lista para que el usuario pueda seleccionar
    for idx, r in enumerate(resultados, 1):
        ciudad = r.get("direccion", {}).get("ciudad", "N/A")
        print(f"{idx}. {r['nombre']} (Ciudad: {ciudad} | Estrellas: {r['categoria_estrellas']})")
    print("-" * 70)

    try:
        seleccion = input("Seleccione el número del hotel para ver su ficha completa (o presione Enter para volver): ").strip()
        if not seleccion:
            return

        idx_sel = int(seleccion) - 1
        if idx_sel < 0 or idx_sel >= len(resultados):
            print("Selección fuera de rango.")
            return

        # Desplegar la ficha de datos detallada del hotel seleccionado
        hotel = resultados[idx_sel]
        print("\n" + "="*60)
        print(f"FICHA DETALLADA: {hotel.get('nombre').upper()}")
        print("="*60)
        print(f"ID en MongoDB:  {hotel['_id']}")
        print(f"Estrellas:      {hotel.get('categoria_estrellas')}")
        print(f"Capacidad:      {hotel.get('capacidad_habitaciones')} habitaciones")
        
        fecha_dt = hotel.get("fecha_inauguracion")
        fecha_str = fecha_dt.strftime('%d-%m-%Y') if fecha_dt else "N/A"
        print(f"Inauguración:   {fecha_str}")
        print(f"Estado Activo:  {'Sí' if hotel.get('activo') else 'No'}")
        
        dir_sub = hotel.get("direccion", {})
        print("\nDIRECCIÓN Y CONTACTO:")
        print(f"  Calle:        {dir_sub.get('calle', 'N/A')}")
        print(f"  Ciudad:       {dir_sub.get('ciudad', 'N/A')}")
        print(f"  País:         {dir_sub.get('pais', 'N/A')}")
        print(f"  Teléfono:     {dir_sub.get('telefono', 'N/A')}")
        
        print("\nHABITACIONES REGISTRADAS:")
        habitaciones = hotel.get("habitaciones", [])
        if not habitaciones:
            print("  No hay habitaciones registradas en este hotel.")
        for hab in habitaciones:
            disp_str = "Disponible" if hab.get("disponible") else "Ocupada"
            print(f"  - Habitación {hab.get('numero')}: Tipo {hab.get('tipo'):<8} | Precio: ${hab.get('precio_noche'):<8} | Estado: {disp_str}")
        print("="*60)

    except ValueError:
        print("[ERROR] Entrada inválida. Debe ingresar un número de la lista.")

# 5. Buscar por rango de fechas
def buscar_por_fecha(collection):
    print("\n--- BUSCAR POR RANGO DE FECHAS (INAUGURACIÓN) ---")
    print("Ingrese la fecha de INICIO:")
    fecha_inicio = leer_fecha()
    print("Ingrese la fecha de FIN:")
    fecha_fin = leer_fecha()

    if fecha_inicio > fecha_fin:
        print("La fecha de inicio es posterior a la de fin. Se intercambiarán automáticamente.")
        fecha_inicio, fecha_fin = fecha_fin, fecha_inicio

    query = {
        "fecha_inauguracion": {
            "$gte": fecha_inicio,
            "$lte": fecha_fin
        }
    }
    
    proyeccion = {"nombre": 1, "fecha_inauguracion": 1, "direccion.ciudad": 1}
    resultados = list(collection.find(query, proyeccion))
    
    print(f"\nHoteles inaugurados entre {fecha_inicio.strftime('%d-%m-%Y')} y {fecha_fin.strftime('%d-%m-%Y')}:")
    print("-" * 70)
    if not resultados:
        print("No se encontraron hoteles en este rango de fechas.")
        return

    for idx, r in enumerate(resultados, 1):
        fecha_dt = r.get("fecha_inauguracion")
        fecha_str = fecha_dt.strftime('%d-%m-%Y') if fecha_dt else "N/A"
        ciudad = r.get("direccion", {}).get("ciudad", "N/A")
        print(f"{idx}. Hotel: {r['nombre']} | Inaugurado: {fecha_str} | Ciudad: {ciudad}")

# 6. Buscar dentro de subdocumento o array de subdocumentos
def buscar_avanzado(collection):
    print("\n--- BÚSQUEDA EN SUBDOCUMENTO O ARRAY ---")
    print("1. Buscar por Ciudad (campo de subdocumento: 'direccion.ciudad')")
    print("2. Buscar por Tipo de Habitación (campo en array de subdocumentos: 'habitaciones.tipo')")
    opcion = input("Seleccione una opción (1-2): ").strip()

    if opcion == "1":
        ciudad = input("Ingrese la ciudad a buscar: ").strip()
        query = {"direccion.ciudad": {"$regex": f"^{ciudad}$", "$options": "i"}}
        proyeccion = {"nombre": 1, "direccion.calle": 1, "direccion.ciudad": 1}
        resultados = list(collection.find(query, proyeccion))
        
        print(f"\nHoteles ubicados en '{ciudad}':")
        print("-" * 60)
        if not resultados:
            print("No se encontraron hoteles en esta ciudad.")
            return
        for idx, r in enumerate(resultados, 1):
            calle = r.get("direccion", {}).get("calle", "")
            print(f"{idx}. Hotel: {r['nombre']} | Dirección: {calle}, {ciudad}")
            
    elif opcion == "2":
        tipo_hab = input("Ingrese tipo de habitación a buscar (Simple / Doble / Suite): ").strip()
        query = {"habitaciones.tipo": {"$regex": f"^{tipo_hab}$", "$options": "i"}}
        proyeccion = {"nombre": 1, "categoria_estrellas": 1, "habitaciones": 1}
        resultados = list(collection.find(query, proyeccion))
        
        print(f"\nHoteles con habitaciones tipo '{tipo_hab}':")
        print("-" * 60)
        if not resultados:
            print(f"No se encontraron hoteles con habitaciones '{tipo_hab}'.")
            return
        for idx, r in enumerate(resultados, 1):
            # Mostrar solo el precio de las habitaciones que coinciden
            precios = [h["precio_noche"] for h in r.get("habitaciones", []) if h.get("tipo").lower() == tipo_hab.lower()]
            precios_str = ", ".join([f"${p}" for p in precios])
            print(f"{idx}. Hotel: {r['nombre']} | Estrellas: {r['categoria_estrellas']} | Precios de '{tipo_hab}': {precios_str}")
    else:
        print("[ERROR] Selección no válida.")

# 7. Actualizar campo del documento raíz
def actualizar_raiz(collection):
    print("\n--- ACTUALIZAR CAMPO DEL DOCUMENTO RAÍZ ---")
    nombre_hotel = input("Ingrese el nombre exacto del hotel a actualizar: ").strip()
    
    # Buscar el documento antes
    hotel = collection.find_one({"nombre": nombre_hotel})
    if not hotel:
        print(f"[ERROR] No se encontró el hotel '{nombre_hotel}'.")
        return
        
    print("\n--- ESTADO ACTUAL DEL HOTEL ---")
    print(f"Nombre: {hotel.get('nombre')}")
    print(f"Estrellas: {hotel.get('categoria_estrellas')}")
    print(f"Capacidad total de habitaciones: {hotel.get('capacidad_habitaciones')}")
    print(f"Activo: {hotel.get('activo')}")
    print("-" * 50)
    
    print("\n¿Qué campo del documento raíz desea actualizar?")
    print("1. Nombre del Hotel")
    print("2. Categoría Estrellas")
    print("3. Capacidad de Habitaciones")
    print("4. Estado Activo (True/False)")
    opcion = input("Opción (1-4): ").strip()
    
    filtro = {"_id": hotel["_id"]}
    update_query = {}
    
    if opcion == "1":
        nuevo_nom = input("Nuevo nombre del hotel: ").strip()
        if nuevo_nom:
            update_query = {"$set": {"nombre": nuevo_nom}}
    elif opcion == "2":
        try:
            nuevas_estrellas = int(input("Nueva categoría (1-5): "))
            update_query = {"$set": {"categoria_estrellas": nuevas_estrellas}}
        except ValueError:
            print("[ERROR] Las estrellas deben ser un número entero.")
            return
    elif opcion == "3":
        try:
            nueva_cap = int(input("Nueva capacidad total de habitaciones: "))
            update_query = {"$set": {"capacidad_habitaciones": nueva_cap}}
        except ValueError:
            print("[ERROR] La capacidad debe ser un número entero.")
            return
    elif opcion == "4":
        nuevo_act = input("¿Está activo? (s/n): ").strip().lower() == 's'
        update_query = {"$set": {"activo": nuevo_act}}
    else:
        print("[ERROR] Opción inválida.")
        return

    if not update_query:
        print("No se realizaron cambios.")
        return

    # Realizar actualización
    collection.update_one(filtro, update_query)
    
    # Mostrar el documento después
    hotel_actualizado = collection.find_one({"_id": hotel["_id"]})
    print("\n[OK] Actualización exitosa. ESTADO ACTUALIZADO DEL HOTEL:")
    print(f"Nombre: {hotel_actualizado.get('nombre')}")
    print(f"Estrellas: {hotel_actualizado.get('categoria_estrellas')}")
    print(f"Capacidad total de habitaciones: {hotel_actualizado.get('capacidad_habitaciones')}")
    print(f"Activo: {hotel_actualizado.get('activo')}")
    print("-" * 50)

# 8. Actualizar dentro de un subdocumento o array
def actualizar_subdocumento_array(collection):
    print("\n--- ACTUALIZAR CAMPO EN SUBDOCUMENTO O ARRAY ---")
    nombre_hotel = input("Ingrese el nombre exacto del hotel a actualizar: ").strip()
    
    # Buscar el documento
    hotel = collection.find_one({"nombre": nombre_hotel})
    if not hotel:
        print(f"[ERROR] No se encontró el hotel '{nombre_hotel}'.")
        return
        
    print("\n--- ESTADO ACTUAL DEL HOTEL ---")
    print(f"Nombre: {hotel.get('nombre')}")
    print(f"Dirección (Subdocumento): {hotel.get('direccion')}")
    print(f"Habitaciones (Array):")
    for hab in hotel.get("habitaciones", []):
        print(f"  - Habitación {hab.get('numero')}: Tipo {hab.get('tipo')} | Precio: ${hab.get('precio_noche')} | Disp: {hab.get('disponible')}")
    print("-" * 50)

    print("\n¿Qué desea actualizar?")
    print("1. Modificar teléfono en la dirección (Subdocumento)")
    print("2. Agregar una nueva habitación al hotel ($push al Array)")
    print("3. Cambiar precio de una habitación específica ($set en Array filtrado)")
    opcion = input("Opción (1-3): ").strip()
    
    filtro = {"_id": hotel["_id"]}
    update_query = {}
    
    if opcion == "1":
        nuevo_tel = input("Ingrese el nuevo teléfono: ").strip()
        update_query = {"$set": {"direccion.telefono": nuevo_tel}}
        
    elif opcion == "2":
        try:
            numero = int(input("Número de la nueva habitación: "))
            tipo = input("Tipo (Simple / Doble / Suite): ").strip()
            precio = float(input("Precio por noche ($): "))
            disponible = input("¿Está disponible? (s/n): ").strip().lower() == 's'
            
            nueva_habitacion = {
                "numero": numero,
                "tipo": tipo,
                "precio_noche": precio,
                "disponible": disponible
            }
            update_query = {"$push": {"habitaciones": nueva_habitacion}}
        except ValueError:
            print("[ERROR] Datos numéricos incorrectos.")
            return
            
    elif opcion == "3":
        try:
            num_hab = int(input("Ingrese el número de la habitación a la que cambiará el precio: "))
            # Validar que exista la habitación en el array local
            habitaciones_nums = [h["numero"] for h in hotel.get("habitaciones", [])]
            if num_hab not in habitaciones_nums:
                print(f"La habitación {num_hab} no existe en este hotel.")
                return
            
            nuevo_precio = float(input("Ingrese el nuevo precio ($): "))
            # Usar operador posicional '$' identificando la habitación adecuada en el filtro
            filtro = {"_id": hotel["_id"], "habitaciones.numero": num_hab}
            update_query = {"$set": {"habitaciones.$.precio_noche": nuevo_precio}}
        except ValueError:
            print("El número o precio debe ser numérico.")
            return
    else:
        print("Opción no válida.")
        return

    # Realizar actualización
    collection.update_one(filtro, update_query)
    
    # Mostrar el documento después
    hotel_actualizado = collection.find_one({"_id": hotel["_id"]})
    print("\n[OK] Actualización exitosa. ESTADO ACTUALIZADO DEL HOTEL:")
    print(f"Nombre: {hotel_actualizado.get('nombre')}")
    print(f"Dirección (Subdocumento): {hotel_actualizado.get('direccion')}")
    print(f"Habitaciones (Array):")
    for hab in hotel_actualizado.get("habitaciones", []):
        print(f"  - Habitación {hab.get('numero')}: Tipo {hab.get('tipo')} | Precio: ${hab.get('precio_noche')} | Disp: {hab.get('disponible')}")
    print("-" * 50)

# 9. Eliminar un hotel
def eliminar_hotel(collection):
    print("\n--- ELIMINAR UN HOTEL ---")
    nombre_hotel = input("Ingrese el nombre exacto del hotel a eliminar: ").strip()
    
    # Muestra el documento a eliminar antes de la operación)
    hotel = collection.find_one({"nombre": nombre_hotel})
    if not hotel:
        print(f"[ERROR] No se encontró el hotel '{nombre_hotel}'.")
        return
        
    print("\n--- DETALLES DEL DOCUMENTO A ELIMINAR ---")
    print(f"Nombre: {hotel.get('nombre')}")
    print(f"Estrellas: {hotel.get('categoria_estrellas')}")
    print(f"Dirección: {hotel.get('direccion', {}).get('calle')}, {hotel.get('direccion', {}).get('ciudad')}")
    print("-" * 50)
    
    # Solicita confirmación
    confirmacion = input("¿Está seguro de que desea eliminar este hotel de forma permanente? (s/n): ").strip().lower()
    if confirmacion == 's':
        resultado = collection.delete_one({"_id": hotel["_id"]})
        if resultado.deleted_count > 0:
            print(f"\n[OK] El hotel '{nombre_hotel}' ha sido eliminado exitosamente.")
        else:
            print("\n[ERROR] No se pudo eliminar el hotel.")
    else:
        print("\nOperación de eliminación cancelada.")

# 10. Agregar reportes
def reporte_agregacion(collection):
    print("\n--- REPORTE ESTADÍSTICO DE PRECIOS POR CIUDAD ---")
    print("Ejecutando pipeline de agregación ($unwind + $group + $sort + $project)...")
    
    # Definición de las etapas de agregación
    pipeline = [
        # Etapa 1: Deshacer el array de habitaciones para analizar los precios individualmente
        {"$unwind": "$habitaciones"},
        
        # Etapa 2: Agrupar por la ciudad de la dirección del hotel
        {
            "$group": {
                "_id": "$direccion.ciudad",
                "precio_promedio_noche": {"$avg": "$habitaciones.precio_noche"},
                "precio_maximo_noche": {"$max": "$habitaciones.precio_noche"},
                "precio_minimo_noche": {"$min": "$habitaciones.precio_noche"},
                "total_habitaciones_analizadas": {"$sum": 1}
            }
        },
        
        # Etapa 3: Ordenar por precio promedio de mayor a menor
        {"$sort": {"precio_promedio_noche": -1}},
        
        # Etapa 4: Proyectar y dar formato final a los campos
        {
            "$project": {
                "_id": 0,
                "ciudad": "$_id",
                "precio_promedio_noche": {"$round": ["$precio_promedio_noche", 0]},
                "precio_maximo_noche": 1,
                "precio_minimo_noche": 1,
                "total_habitaciones_analizadas": 1
            }
        }
    ]
    
    try:
        resultados = list(collection.aggregate(pipeline))
        
        if not resultados:
            print("No hay datos de habitaciones suficientes para generar el reporte.")
            return

        print("\n" + "="*85)
        print(f"{'Ciudad':<20} | {'Hab. Analizadas':<15} | {'Precio Promedio':<15} | {'Precio Mínimo':<13} | {'Precio Máximo':<13}")
        print("="*85)
        for r in resultados:
            print(f"{r['ciudad']:<20} | {r['total_habitaciones_analizadas']:<15} | ${r['precio_promedio_noche']:<14} | ${r['precio_minimo_noche']:<12} | ${r['precio_maximo_noche']:<12}")
        print("="*85 + "\n")
        
    except Exception as e:
        print(f"[ERROR] Error al ejecutar el pipeline de agregación: {e}")

def main():
    client, collection = connect_db()
    
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (0-10): ").strip()
        
        if opcion == "1":
            crear_hotel(collection)
        elif opcion == "2":
            listar_hoteles(collection)
        elif opcion == "3":
            buscar_por_estrellas(collection)
        elif opcion == "4":
            buscar_por_regex(collection)
        elif opcion == "5":
            buscar_por_fecha(collection)
        elif opcion == "6":
            buscar_avanzado(collection)
        elif opcion == "7":
            actualizar_raiz(collection)
        elif opcion == "8":
            actualizar_subdocumento_array(collection)
        elif opcion == "9":
            eliminar_hotel(collection)
        elif opcion == "10":
            reporte_agregacion(collection)
        elif opcion == "0":
            print("\nGracias por utilizar el sistema de gestión de hoteles. ¡Hasta pronto!\n")
            client.close()
            break
        else:
            print("[ERROR] Opción no válida. Intente de nuevo.")
            
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()
