import os
import sqlite3
import logging
from datetime import datetime
from extraer_rcg_sevilla import extraer_informacion_campo

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/importar_rcg_sevilla.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("importar_rcg_sevilla")

def verificar_tablas(conn):
    """
    Verifica que las tablas necesarias existan en la base de datos
    """
    cursor = conn.cursor()
    
    # Verificar si existen las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='campos'")
    if not cursor.fetchone():
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
        logger.info("Tabla 'campos' creada")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recorridos'")
    if not cursor.fetchone():
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
        logger.info("Tabla 'recorridos' creada")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='barras'")
    if not cursor.fetchone():
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
        logger.info("Tabla 'barras' creada")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hoyos'")
    if not cursor.fetchone():
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
        logger.info("Tabla 'hoyos' creada")
    
    conn.commit()
    logger.info("Verificación de tablas completada")

def importar_campo_rcg_sevilla(db_path):
    """
    Importa la información del campo RCG Sevilla a la base de datos
    """
    # Extraer información del campo
    archivo_html = "output/paginas_campos/campo_444.html"
    info_campo = extraer_informacion_campo(archivo_html)
    
    if not info_campo:
        logger.error("No se pudo extraer la información del campo")
        return False
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar tablas
        verificar_tablas(conn)
        
        # Verificar si el campo ya existe
        cursor.execute("SELECT id FROM campos WHERE nombre = ?", (info_campo['nombre'],))
        campo_existente = cursor.fetchone()
        
        if campo_existente:
            id_campo = campo_existente[0]
            logger.info(f"Campo '{info_campo['nombre']}' ya existe con ID {id_campo}")
        else:
            # Insertar el campo
            cursor.execute('''
            INSERT INTO campos (
                nombre, ciudad, provincia, hoyos_totales, id_rfeg, ultima_actualizacion
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                info_campo['nombre'],
                info_campo.get('ciudad', ''),
                info_campo.get('provincia', ''),
                18,  # Hoyos totales
                "444",  # ID RFEG
                datetime.now().isoformat()
            ))
            
            id_campo = cursor.lastrowid
            logger.info(f"Campo '{info_campo['nombre']}' insertado con ID {id_campo}")
        
        # Procesar recorridos
        if 'recorridos' in info_campo:
            for recorrido_info in info_campo['recorridos']:
                # Verificar si el recorrido ya existe
                cursor.execute(
                    "SELECT id FROM recorridos WHERE id_campo = ? AND nombre = ?",
                    (id_campo, recorrido_info['nombre'])
                )
                recorrido_existente = cursor.fetchone()
                
                if recorrido_existente:
                    id_recorrido = recorrido_existente[0]
                    logger.info(f"Recorrido '{recorrido_info['nombre']}' ya existe con ID {id_recorrido}")
                else:
                    # Insertar el recorrido
                    cursor.execute('''
                    INSERT INTO recorridos (id_campo, id_recorrido, nombre)
                    VALUES (?, ?, ?)
                    ''', (
                        id_campo,
                        recorrido_info['nombre'].lower(),  # Usar el nombre en minúsculas como id_recorrido
                        recorrido_info['nombre']
                    ))
                    
                    id_recorrido = cursor.lastrowid
                    logger.info(f"Recorrido '{recorrido_info['nombre']}' insertado con ID {id_recorrido}")
                
                # Verificar si la barra ya existe
                cursor.execute(
                    "SELECT id FROM barras WHERE id_recorrido = ? AND nombre = ?",
                    (id_recorrido, recorrido_info['nombre'])
                )
                barra_existente = cursor.fetchone()
                
                if barra_existente:
                    id_barra = barra_existente[0]
                    logger.info(f"Barra '{recorrido_info['nombre']}' ya existe con ID {id_barra}")
                    
                    # Actualizar la barra existente
                    cursor.execute('''
                    UPDATE barras
                    SET valor_campo = ?, slope = ?
                    WHERE id = ?
                    ''', (
                        recorrido_info.get('valor_campo', None),
                        recorrido_info.get('slope', None),
                        id_barra
                    ))
                    logger.info(f"Barra '{recorrido_info['nombre']}' actualizada")
                else:
                    # Insertar la barra
                    cursor.execute('''
                    INSERT INTO barras (id_recorrido, nombre, valor_campo, slope)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        id_recorrido,
                        recorrido_info['nombre'],
                        recorrido_info.get('valor_campo', None),
                        recorrido_info.get('slope', None)
                    ))
                    
                    id_barra = cursor.lastrowid
                    logger.info(f"Barra '{recorrido_info['nombre']}' insertada con ID {id_barra}")
                
                # Procesar hoyos
                if 'hoyos' in recorrido_info:
                    # Eliminar hoyos existentes para esta barra
                    cursor.execute("DELETE FROM hoyos WHERE id_barra = ?", (id_barra,))
                    
                    # Insertar los nuevos hoyos
                    for hoyo_info in recorrido_info['hoyos']:
                        cursor.execute('''
                        INSERT INTO hoyos (id_barra, numero, par, metros, hcp)
                        VALUES (?, ?, ?, ?, ?)
                        ''', (
                            id_barra,
                            hoyo_info['numero'],
                            hoyo_info.get('par', 0),
                            hoyo_info.get('metros', 0),
                            hoyo_info.get('hcp', 0)
                        ))
                    
                    logger.info(f"Insertados {len(recorrido_info['hoyos'])} hoyos para la barra '{recorrido_info['nombre']}'")
        
        conn.commit()
        logger.info("Importación completada con éxito")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error durante la importación: {str(e)}")
        return False
    
    finally:
        conn.close()

def main():
    # Crear directorio de logs si no existe
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Ruta a la base de datos
    db_path = "golf_scorecard.db"
    
    # Importar campo
    resultado = importar_campo_rcg_sevilla(db_path)
    
    if resultado:
        logger.info("Proceso de importación completado correctamente")
    else:
        logger.error("El proceso de importación falló")

if __name__ == "__main__":
    main()
