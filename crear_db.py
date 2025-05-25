import sqlite3
import json
import os
import datetime

def crear_base_datos():
    """
    Crea la base de datos SQLite para almacenar la información de los campos de golf.
    """
    # Verificar si existe el directorio de la base de datos
    db_dir = "db"
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Ruta de la base de datos
    db_path = os.path.join(db_dir, "campos_golf.db")
    
    # Conectar a la base de datos (la crea si no existe)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear la tabla de campos de golf
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS campos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        ciudad TEXT,
        provincia TEXT,
        hoyos_totales INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        json_pares TEXT,            -- JSON con los pares de cada hoyo
        json_handicaps TEXT,        -- JSON con los handicaps de cada hoyo
        valor_campo REAL,           -- VC (Course Rating)
        par_campo INTEGER,          -- Par total del campo
        slope REAL,                 -- Valor Slope (VS)
        id_rfeg TEXT UNIQUE,        -- ID del campo en la RFEG
        url TEXT,                   -- URL del campo en la RFEG
        recorridos_disponibles TEXT, -- JSON con info de recorridos disponibles
        ultima_actualizacion DATETIME -- Fecha de última actualización de datos
    )
    ''')
    
    # Crear tabla para los recorridos de cada campo
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recorridos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_campo INTEGER,
        id_recorrido TEXT,
        nombre TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_campo) REFERENCES campos(id),
        UNIQUE(id_campo, id_recorrido)
    )
    ''')
    
    # Crear tabla para las barras de cada recorrido
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS barras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_recorrido INTEGER,
        nombre TEXT NOT NULL,
        valor_campo REAL,           -- VC (Course Rating) específico de la barra
        slope REAL,                 -- Valor Slope (VS) específico de la barra
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_recorrido) REFERENCES recorridos(id),
        UNIQUE(id_recorrido, nombre)
    )
    ''')
    
    # Crear tabla para los hoyos de cada barra
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hoyos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_barra INTEGER,
        numero INTEGER NOT NULL,
        metros INTEGER,
        par INTEGER,
        hcp INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_barra) REFERENCES barras(id),
        UNIQUE(id_barra, numero)
    )
    ''')
    
    # Guardar los cambios y cerrar la conexión
    conn.commit()
    conn.close()
    
    print(f"Base de datos creada en: {db_path}")

def insertar_campo_ejemplo():
    """
    Inserta un campo de ejemplo en la base de datos para demostrar la estructura.
    """
    db_path = os.path.join("db", "campos_golf.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Datos de ejemplo para un campo
    nombre = "Real Club de Golf de Sevilla"
    ciudad = "ALCALA DE GUADAIRA"
    provincia = "SEVILLA"
    hoyos_totales = 18
    id_rfeg = "444"
    url = "https://rfegolf.es/ClubPaginas/ClubMicrosite.aspx?ClubId=444"
    
    # JSON con los pares de cada hoyo (ejemplo)
    json_pares = json.dumps({
        "1": 4, "2": 4, "3": 3, "4": 4, "5": 5, "6": 4, "7": 3, "8": 5, "9": 4,
        "10": 4, "11": 4, "12": 3, "13": 5, "14": 4, "15": 4, "16": 3, "17": 5, "18": 4
    })
    
    # JSON con los handicaps de cada hoyo (ejemplo)
    json_handicaps = json.dumps({
        "1": 14, "2": 2, "3": 12, "4": 6, "5": 18, "6": 4, "7": 16, "8": 8, "9": 10,
        "10": 13, "11": 1, "12": 17, "13": 5, "14": 7, "15": 3, "16": 15, "17": 9, "18": 11
    })
    
    # Valores de ejemplo
    valor_campo = 72.5  # VC (Course Rating)
    par_campo = 72      # Par total del campo
    slope = 133         # Valor Slope (VS)
    
    # Información de recorridos disponibles
    recorridos_disponibles = json.dumps([{"id": "2082", "nombre": "RCG SEVILLA"}])
    
    # Fecha actual
    ultima_actualizacion = datetime.datetime.now().isoformat()
    
    # Insertar el campo
    cursor.execute('''
    INSERT INTO campos (
        nombre, ciudad, provincia, hoyos_totales, json_pares, json_handicaps,
        valor_campo, par_campo, slope, id_rfeg, url, recorridos_disponibles, ultima_actualizacion
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        nombre, ciudad, provincia, hoyos_totales, json_pares, json_handicaps,
        valor_campo, par_campo, slope, id_rfeg, url, recorridos_disponibles, ultima_actualizacion
    ))
    
    # Obtener el ID del campo insertado
    id_campo = cursor.lastrowid
    
    # Insertar un recorrido
    cursor.execute('''
    INSERT INTO recorridos (id_campo, id_recorrido, nombre)
    VALUES (?, ?, ?)
    ''', (id_campo, "2082", "RCG SEVILLA"))
    
    # Obtener el ID del recorrido insertado
    id_recorrido = cursor.lastrowid
    
    # Insertar barras
    barras = ["NEGRAS", "BLANCAS", "AMARILLAS", "ROJAS", "NARANJAS", "VERDES"]
    valores_campo = [73.5, 72.5, 71.5, 70.5, 69.5, 68.5]  # Valores de ejemplo
    slopes = [135, 133, 130, 128, 125, 122]  # Valores de ejemplo
    
    for i, barra in enumerate(barras):
        cursor.execute('''
        INSERT INTO barras (id_recorrido, nombre, valor_campo, slope)
        VALUES (?, ?, ?, ?)
        ''', (id_recorrido, barra, valores_campo[i], slopes[i]))
        
        # Obtener el ID de la barra insertada
        id_barra = cursor.lastrowid
        
        # Insertar hoyos para esta barra (datos de ejemplo)
        for hoyo in range(1, 19):
            # Valores de ejemplo para cada hoyo
            metros = 300 + (hoyo * 10)
            par = 4 if hoyo % 3 != 0 else (3 if hoyo % 6 == 0 else 5)
            hcp = hoyo if hoyo <= 18 else (hoyo - 18)
            
            cursor.execute('''
            INSERT INTO hoyos (id_barra, numero, metros, par, hcp)
            VALUES (?, ?, ?, ?, ?)
            ''', (id_barra, hoyo, metros, par, hcp))
    
    # Guardar los cambios y cerrar la conexión
    conn.commit()
    conn.close()
    
    print(f"Campo de ejemplo insertado con ID: {id_campo}")

def mostrar_estructura_db():
    """
    Muestra la estructura de la base de datos.
    """
    db_path = os.path.join("db", "campos_golf.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    
    print("\nEstructura de la base de datos:")
    print("==============================")
    
    for tabla in tablas:
        nombre_tabla = tabla[0]
        print(f"\nTabla: {nombre_tabla}")
        print("-" * (len(nombre_tabla) + 7))
        
        # Obtener información de las columnas
        cursor.execute(f"PRAGMA table_info({nombre_tabla})")
        columnas = cursor.fetchall()
        
        for columna in columnas:
            cid, nombre, tipo, notnull, dflt_value, pk = columna
            pk_str = "PRIMARY KEY" if pk else ""
            notnull_str = "NOT NULL" if notnull else ""
            print(f"  {nombre} ({tipo}) {pk_str} {notnull_str}")
    
    conn.close()

if __name__ == "__main__":
    # Crear la base de datos
    crear_base_datos()
    
    # Insertar un campo de ejemplo
    insertar_campo_ejemplo()
    
    # Mostrar la estructura de la base de datos
    mostrar_estructura_db()
