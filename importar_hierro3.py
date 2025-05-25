import sqlite3
import json
import os
import logging
from datetime import datetime

def configurar_logging():
    # Crear directorio de logs si no existe
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar el logger principal
    logger = logging.getLogger('importar_hierro3')
    logger.setLevel(logging.INFO)
    
    # Crear un formateador para los logs
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Crear un manejador para el archivo de log general
    fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'importar_hierro3_{fecha_actual}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Crear un manejador para la consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Agregar los manejadores al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def crear_base_datos(db_path, logger):
    """
    Crea una nueva base de datos con las tablas necesarias.
    """
    try:
        # Eliminar la base de datos si ya existe
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Base de datos existente eliminada: {db_path}")
        
        # Crear una nueva conexión a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tabla de campos
        cursor.execute('''
        CREATE TABLE campos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            ciudad TEXT,
            provincia TEXT,
            hoyos_totales INTEGER,
            json_pares TEXT,
            json_handicaps TEXT,
            par_campo INTEGER,
            id_rfeg TEXT,
            url TEXT,
            recorridos_disponibles TEXT,
            ultima_actualizacion TEXT
        )
        ''')
        
        # Crear tabla de recorridos
        cursor.execute('''
        CREATE TABLE recorridos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_campo INTEGER,
            id_recorrido TEXT,
            nombre TEXT,
            FOREIGN KEY (id_campo) REFERENCES campos (id)
        )
        ''')
        
        # Crear tabla de barras
        cursor.execute('''
        CREATE TABLE barras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_recorrido INTEGER,
            nombre TEXT,
            valor_campo REAL,
            slope REAL,
            FOREIGN KEY (id_recorrido) REFERENCES recorridos (id)
        )
        ''')
        
        # Crear tabla de hoyos
        cursor.execute('''
        CREATE TABLE hoyos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_barra INTEGER,
            numero INTEGER,
            metros INTEGER,
            par INTEGER,
            hcp INTEGER,
            FOREIGN KEY (id_barra) REFERENCES barras (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Base de datos creada correctamente")
        
    except Exception as e:
        logger.error(f"Error al crear la base de datos: {e}", exc_info=True)
        raise

def importar_hierro3(db_path, logger):
    """
    Importa los datos del campo Hierro 3 a la base de datos.
    """
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Datos del campo Hierro 3
        id_rfeg = "710"
        nombre_campo = "CLUB DEPORTIVO DE GOLF HIERRO 3 REINO DE LEON"
        ciudad = "VILLANUEVA DEL ARBOL"
        provincia = "LEON"
        hoyos_totales = 18
        
        # Insertar el campo en la base de datos
        cursor.execute('''
        INSERT INTO campos (
            nombre, ciudad, provincia, hoyos_totales, id_rfeg, ultima_actualizacion
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            nombre_campo,
            ciudad,
            provincia,
            hoyos_totales,
            id_rfeg,
            datetime.now().isoformat()
        ))
        
        id_campo = cursor.lastrowid
        logger.info(f"Campo insertado con ID: {id_campo}")
        
        # Insertar el recorrido
        nombre_recorrido = "HIERRO 3"
        id_recorrido = "1"
        
        cursor.execute('''
        INSERT INTO recorridos (id_campo, id_recorrido, nombre)
        VALUES (?, ?, ?)
        ''', (id_campo, id_recorrido, nombre_recorrido))
        
        id_rec = cursor.lastrowid
        logger.info(f"Recorrido insertado: {nombre_recorrido}")
        
        # Insertar las barras y hoyos
        # Datos de las barras AMARILLAS
        barras = [
            {
                "nombre": "AMARILLAS",
                "valor_campo": 66.0,
                "slope": 119.0,
                "hoyos": [
                    {"numero": 1, "metros": 438, "par": 5, "hcp": 9},
                    {"numero": 2, "metros": 275, "par": 4, "hcp": 13},
                    {"numero": 3, "metros": 140, "par": 3, "hcp": 10},
                    {"numero": 4, "metros": 247, "par": 4, "hcp": 4},
                    {"numero": 5, "metros": 231, "par": 4, "hcp": 5},
                    {"numero": 6, "metros": 454, "par": 5, "hcp": 1},
                    {"numero": 7, "metros": 150, "par": 3, "hcp": 8},
                    {"numero": 8, "metros": 287, "par": 4, "hcp": 6},
                    {"numero": 9, "metros": 270, "par": 4, "hcp": 17},
                    {"numero": 10, "metros": 354, "par": 4, "hcp": 2},
                    {"numero": 11, "metros": 271, "par": 4, "hcp": 16},
                    {"numero": 12, "metros": 138, "par": 3, "hcp": 14},
                    {"numero": 13, "metros": 222, "par": 4, "hcp": 15},
                    {"numero": 14, "metros": 224, "par": 4, "hcp": 7},
                    {"numero": 15, "metros": 438, "par": 5, "hcp": 3},
                    {"numero": 16, "metros": 137, "par": 3, "hcp": 12},
                    {"numero": 17, "metros": 268, "par": 4, "hcp": 11},
                    {"numero": 18, "metros": 254, "par": 4, "hcp": 18}
                ]
            },
            {
                "nombre": "ROJAS",
                "valor_campo": 63.4,
                "slope": 105.0,
                "hoyos": [
                    {"numero": 1, "metros": 384, "par": 5, "hcp": 9},
                    {"numero": 2, "metros": 244, "par": 4, "hcp": 13},
                    {"numero": 3, "metros": 110, "par": 3, "hcp": 10},
                    {"numero": 4, "metros": 232, "par": 4, "hcp": 4},
                    {"numero": 5, "metros": 205, "par": 4, "hcp": 5},
                    {"numero": 6, "metros": 409, "par": 5, "hcp": 1},
                    {"numero": 7, "metros": 118, "par": 3, "hcp": 8},
                    {"numero": 8, "metros": 241, "par": 4, "hcp": 6},
                    {"numero": 9, "metros": 207, "par": 4, "hcp": 17},
                    {"numero": 10, "metros": 332, "par": 4, "hcp": 2},
                    {"numero": 11, "metros": 254, "par": 4, "hcp": 16},
                    {"numero": 12, "metros": 90, "par": 3, "hcp": 14},
                    {"numero": 13, "metros": 209, "par": 4, "hcp": 15},
                    {"numero": 14, "metros": 194, "par": 4, "hcp": 7},
                    {"numero": 15, "metros": 398, "par": 5, "hcp": 3},
                    {"numero": 16, "metros": 101, "par": 3, "hcp": 12},
                    {"numero": 17, "metros": 226, "par": 4, "hcp": 11},
                    {"numero": 18, "metros": 197, "par": 4, "hcp": 18}
                ]
            }
        ]
        
        # Calcular par del campo
        par_campo = sum(hoyo["par"] for hoyo in barras[0]["hoyos"])
        
        # Actualizar el par del campo
        cursor.execute('''
        UPDATE campos SET par_campo = ? WHERE id = ?
        ''', (par_campo, id_campo))
        
        # Crear JSON de pares y handicaps
        json_pares = {str(hoyo["numero"]): hoyo["par"] for hoyo in barras[0]["hoyos"]}
        json_handicaps = {str(hoyo["numero"]): hoyo["hcp"] for hoyo in barras[0]["hoyos"]}
        
        # Actualizar JSON de pares y handicaps
        cursor.execute('''
        UPDATE campos SET json_pares = ?, json_handicaps = ? WHERE id = ?
        ''', (json.dumps(json_pares), json.dumps(json_handicaps), id_campo))
        
        # Insertar las barras y hoyos
        for barra in barras:
            nombre_barra = barra["nombre"]
            valor_campo = barra["valor_campo"]
            slope = barra["slope"]
            
            # Insertar la barra
            cursor.execute('''
            INSERT INTO barras (id_recorrido, nombre, valor_campo, slope)
            VALUES (?, ?, ?, ?)
            ''', (id_rec, nombre_barra, valor_campo, slope))
            
            id_barra = cursor.lastrowid
            logger.info(f"Barra insertada: {nombre_barra}")
            
            # Insertar los hoyos
            for hoyo in barra["hoyos"]:
                numero = hoyo["numero"]
                metros = hoyo["metros"]
                par = hoyo["par"]
                hcp = hoyo["hcp"]
                
                cursor.execute('''
                INSERT INTO hoyos (id_barra, numero, metros, par, hcp)
                VALUES (?, ?, ?, ?, ?)
                ''', (id_barra, numero, metros, par, hcp))
            
            logger.info(f"Insertados {len(barra['hoyos'])} hoyos para la barra {nombre_barra}")
        
        # Guardar los cambios y cerrar la conexión
        conn.commit()
        conn.close()
        
        logger.info("Datos del campo Hierro 3 importados correctamente")
        
    except Exception as e:
        logger.error(f"Error al importar los datos del campo Hierro 3: {e}", exc_info=True)
        raise

def consultar_datos(db_path, logger):
    """
    Consulta y muestra los datos importados para verificar su consistencia.
    """
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Consultar campos
        logger.info("=== CAMPOS ===")
        cursor.execute("SELECT id, nombre, ciudad, provincia, hoyos_totales, par_campo FROM campos")
        for campo in cursor.fetchall():
            logger.info(f"ID: {campo[0]}, Nombre: {campo[1]}, Ciudad: {campo[2]}, Provincia: {campo[3]}, Hoyos: {campo[4]}, Par: {campo[5]}")
        
        # Consultar recorridos
        logger.info("\n=== RECORRIDOS ===")
        cursor.execute("SELECT id, id_campo, nombre FROM recorridos")
        for recorrido in cursor.fetchall():
            logger.info(f"ID: {recorrido[0]}, ID Campo: {recorrido[1]}, Nombre: {recorrido[2]}")
        
        # Consultar barras
        logger.info("\n=== BARRAS ===")
        cursor.execute("""
        SELECT b.id, r.nombre, b.nombre, b.valor_campo, b.slope 
        FROM barras b
        JOIN recorridos r ON b.id_recorrido = r.id
        """)
        for barra in cursor.fetchall():
            logger.info(f"ID: {barra[0]}, Recorrido: {barra[1]}, Barra: {barra[2]}, Valoración: {barra[3]}, Slope: {barra[4]}")
        
        # Consultar hoyos (muestra solo algunos para no saturar la salida)
        logger.info("\n=== HOYOS (muestra parcial) ===")
        cursor.execute("""
        SELECT h.id, b.nombre, h.numero, h.metros, h.par, h.hcp 
        FROM hoyos h
        JOIN barras b ON h.id_barra = b.id
        ORDER BY b.nombre, h.numero
        LIMIT 10
        """)
        for hoyo in cursor.fetchall():
            logger.info(f"Barra: {hoyo[1]}, Hoyo: {hoyo[2]}, Metros: {hoyo[3]}, Par: {hoyo[4]}, HCP: {hoyo[5]}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error al consultar los datos: {e}", exc_info=True)
        raise

def main():
    # Configurar logging
    logger = configurar_logging()
    
    # Ruta a la base de datos
    db_path = "golf_scorecard.db"
    
    try:
        # Crear la base de datos
        crear_base_datos(db_path, logger)
        
        # Importar los datos del campo Hierro 3
        importar_hierro3(db_path, logger)
        
        # Consultar los datos para verificar su consistencia
        consultar_datos(db_path, logger)
        
        logger.info("Proceso completado correctamente")
        
    except Exception as e:
        logger.error(f"Error en el proceso: {e}", exc_info=True)

if __name__ == "__main__":
    main()
