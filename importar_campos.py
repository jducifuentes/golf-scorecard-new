import sqlite3
import json
import os
import datetime
import glob
import logging
from datetime import datetime

# Configurar el sistema de logging
def configurar_logging():
    # Crear directorio de logs si no existe
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar el logger principal
    logger = logging.getLogger('importar_campos')
    logger.setLevel(logging.INFO)
    
    # Crear un formateador para los logs
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Crear un manejador para el archivo de log general
    fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'importar_campos_{fecha_actual}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Crear un manejador para el archivo de log de errores
    error_log_file = os.path.join(log_dir, f'importar_campos_errores_{fecha_actual}.log')
    error_file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    
    # Crear un manejador para la consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Agregar los manejadores al logger
    logger.addHandler(file_handler)
    logger.addHandler(error_file_handler)
    logger.addHandler(console_handler)
    
    return logger

def importar_campo(archivo_json, db_path, logger):
    """
    Importa la información de un campo de golf desde un archivo JSON a la base de datos SQLite.
    
    Args:
        archivo_json (str): Ruta al archivo JSON con la información del campo.
        db_path (str): Ruta a la base de datos SQLite.
        logger: Logger para registrar el proceso.
    
    Returns:
        int: ID del campo importado en la base de datos.
    """
    try:
        # Cargar datos del archivo JSON
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Extraer información básica del campo
        url = datos.get('url', '')
        id_rfeg = datos.get('id', '')
        
        # Verificar si el campo ya existe en la base de datos
        cursor.execute('SELECT id FROM campos WHERE id_rfeg = ?', (id_rfeg,))
        resultado = cursor.fetchone()
        
        if resultado:
            # El campo ya existe, actualizar la información
            id_campo = resultado[0]
            logger.info(f"Actualizando campo existente con ID: {id_campo}")
        else:
            # Obtener información adicional del campo desde el archivo campos_golf.json
            info_campo = obtener_info_campo(id_rfeg)
            
            # Extraer recorridos disponibles
            recorridos = datos.get('recorridos', [])
            recorridos_disponibles = json.dumps([
                {"id": rec.get('id', ''), "nombre": rec.get('nombre', '')}
                for rec in recorridos
            ])
            
            # Calcular par del campo y handicaps (tomando el primer recorrido y la primera barra si existen)
            par_campo = 0
            json_pares = {}
            json_handicaps = {}
            
            if recorridos and 'barras' in recorridos[0] and recorridos[0]['barras']:
                # Buscar la primera barra que tenga hoyos
                primera_barra = None
                for barra in recorridos[0]['barras']:
                    if barra.get('hoyos'):
                        primera_barra = barra
                        break
                
                if primera_barra:
                    for hoyo in primera_barra.get('hoyos', []):
                        numero = hoyo.get('numero')
                        par = int(hoyo.get('par', 0))
                        hcp = int(hoyo.get('hcp', 0))
                        
                        if numero:
                            json_pares[str(numero)] = par
                            json_handicaps[str(numero)] = hcp
                            par_campo += par
            
            # Insertar el campo en la base de datos
            cursor.execute('''
            INSERT INTO campos (
                nombre, ciudad, provincia, hoyos_totales, json_pares, json_handicaps,
                par_campo, id_rfeg, url, recorridos_disponibles, ultima_actualizacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                info_campo.get('nombre', ''),
                info_campo.get('ciudad', ''),
                info_campo.get('provincia', ''),
                info_campo.get('hoyos', 0),
                json.dumps(json_pares),
                json.dumps(json_handicaps),
                par_campo,
                id_rfeg,
                url,
                recorridos_disponibles,
                datetime.now().isoformat()
            ))
            
            # Obtener el ID del campo insertado
            id_campo = cursor.lastrowid
            logger.info(f"Campo insertado con ID: {id_campo}")
        
        # Procesar los recorridos
        for recorrido in datos.get('recorridos', []):
            id_recorrido = recorrido.get('id', '')
            nombre_recorrido = recorrido.get('nombre', '')
            
            # Verificar si el recorrido ya existe
            cursor.execute('''
            SELECT id FROM recorridos 
            WHERE id_campo = ? AND id_recorrido = ?
            ''', (id_campo, id_recorrido))
            
            resultado = cursor.fetchone()
            
            if resultado:
                # El recorrido ya existe, obtener su ID
                id_rec = resultado[0]
                logger.info(f"  Actualizando recorrido existente: {nombre_recorrido}")
                
                # Eliminar las barras existentes para este recorrido
                cursor.execute('''
                DELETE FROM barras WHERE id_recorrido IN (
                    SELECT id FROM recorridos WHERE id_campo = ? AND id_recorrido = ?
                )
                ''', (id_campo, id_recorrido))
            else:
                # Insertar el recorrido
                cursor.execute('''
                INSERT INTO recorridos (id_campo, id_recorrido, nombre)
                VALUES (?, ?, ?)
                ''', (id_campo, id_recorrido, nombre_recorrido))
                
                id_rec = cursor.lastrowid
                logger.info(f"  Recorrido insertado: {nombre_recorrido}")
            
            # Procesar las barras
            for barra in recorrido.get('barras', []):
                nombre_barra = barra.get('nombre', '')
                
                # Verificar si la barra ya existe
                cursor.execute('''
                SELECT id FROM barras 
                WHERE id_recorrido = ? AND nombre = ?
                ''', (id_rec, nombre_barra))
                
                resultado = cursor.fetchone()
                
                if resultado:
                    # La barra ya existe, obtener su ID
                    id_barra = resultado[0]
                    logger.info(f"    Actualizando barra existente: {nombre_barra}")
                    
                    # Eliminar los hoyos existentes para esta barra
                    cursor.execute('DELETE FROM hoyos WHERE id_barra = ?', (id_barra,))
                else:
                    # Insertar la barra
                    valoracion = barra.get('valoracion', '')
                    slope = barra.get('slope', '')
                    
                    # Asegurarse de que los valores sean numéricos
                    if isinstance(valoracion, str) and valoracion:
                        try:
                            # Si es una cadena con coma como separador decimal, reemplazar por punto
                            valoracion = valoracion.replace(',', '.')
                            valoracion = float(valoracion)
                        except ValueError:
                            valoracion = ''
                    
                    if isinstance(slope, str) and slope:
                        try:
                            slope = float(slope)
                        except ValueError:
                            slope = ''
                    
                    cursor.execute('''
                    INSERT INTO barras (id_recorrido, nombre, valor_campo, slope)
                    VALUES (?, ?, ?, ?)
                    ''', (id_rec, nombre_barra, valoracion, slope))
                    
                    id_barra = cursor.lastrowid
                    logger.info(f"    Barra insertada: {nombre_barra}")
                
                # Procesar los hoyos
                for hoyo in barra.get('hoyos', []):
                    numero = hoyo.get('numero')
                    metros = int(hoyo.get('metros', 0))
                    par = int(hoyo.get('par', 0))
                    hcp = int(hoyo.get('hcp', 0))
                    
                    # Insertar el hoyo
                    cursor.execute('''
                    INSERT INTO hoyos (id_barra, numero, metros, par, hcp)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (id_barra, numero, metros, par, hcp))
        
        # Guardar los cambios y cerrar la conexión
        conn.commit()
        conn.close()
        
        return id_campo
    
    except Exception as e:
        logger.error(f"Error al importar el campo desde {archivo_json}: {e}", exc_info=True)
        raise

def obtener_info_campo(id_rfeg):
    """
    Obtiene información adicional del campo desde el archivo campos_golf.json.
    
    Args:
        id_rfeg (str): ID del campo en la RFEG.
    
    Returns:
        dict: Información del campo.
    """
    try:
        with open('output/campos_golf.json', 'r', encoding='utf-8') as f:
            campos = json.load(f)
        
        for campo in campos:
            if campo.get('id') == id_rfeg:
                return campo
    except Exception as e:
        print(f"Error al obtener información del campo: {e}")
    
    return {}

def importar_todos_campos():
    """
    Importa todos los campos de golf disponibles en la carpeta output/campos.
    """
    # Configurar el sistema de logging
    logger = configurar_logging()
    
    # Verificar si existe el directorio de la base de datos
    db_dir = "db"
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Ruta de la base de datos
    db_path = os.path.join(db_dir, "campos_golf.db")
    
    # Verificar si la base de datos existe, si no, crearla
    if not os.path.exists(db_path):
        logger.error("La base de datos no existe. Ejecute primero crear_db.py")
        return
    
    # Buscar todos los archivos JSON de campos en la carpeta output/campos
    patron = os.path.join('output', 'campos', 'campo_*.json')
    archivos = glob.glob(patron)
    
    if not archivos:
        logger.warning("No se encontraron archivos JSON de campos en la carpeta output/campos.")
        return
    
    logger.info(f"Se encontraron {len(archivos)} archivos JSON de campos.")
    
    # Importar cada campo
    campos_importados = 0
    campos_con_error = 0
    
    for archivo in archivos:
        logger.info(f"\nImportando campo desde: {archivo}")
        try:
            id_campo = importar_campo(archivo, db_path, logger)
            logger.info(f"Campo importado correctamente con ID: {id_campo}")
            campos_importados += 1
        except Exception as e:
            logger.error(f"Error al importar el campo desde {archivo}: {e}")
            campos_con_error += 1
    
    logger.info(f"\nProceso de importación completado.")
    logger.info(f"Campos importados correctamente: {campos_importados}")
    logger.info(f"Campos con errores: {campos_con_error}")

def mostrar_campos_importados():
    """
    Muestra un resumen de los campos importados en la base de datos.
    """
    # Configurar el sistema de logging
    logger = configurar_logging()
    
    db_path = os.path.join("db", "campos_golf.db")
    
    if not os.path.exists(db_path):
        logger.error("La base de datos no existe.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obtener todos los campos
    cursor.execute('''
    SELECT c.id, c.nombre, c.ciudad, c.provincia, c.hoyos_totales, c.par_campo,
           COUNT(DISTINCT r.id) as num_recorridos,
           COUNT(DISTINCT b.id) as num_barras,
           COUNT(DISTINCT h.id) as num_hoyos
    FROM campos c
    LEFT JOIN recorridos r ON c.id = r.id_campo
    LEFT JOIN barras b ON r.id = b.id_recorrido
    LEFT JOIN hoyos h ON b.id = h.id_barra
    GROUP BY c.id
    ORDER BY c.nombre
    ''')
    
    campos = cursor.fetchall()
    
    logger.info("\nCampos importados en la base de datos:")
    logger.info("=====================================")
    
    if not campos:
        logger.warning("No hay campos importados en la base de datos.")
    else:
        logger.info(f"{'ID':<4} {'Nombre':<30} {'Ciudad':<20} {'Provincia':<15} {'Hoyos':<6} {'Par':<4} {'Rec.':<5} {'Barras':<7} {'Hoyos':<6}")
        logger.info("-" * 100)
        
        for campo in campos:
            id_campo, nombre, ciudad, provincia, hoyos, par, num_rec, num_barras, num_hoyos = campo
            logger.info(f"{id_campo:<4} {nombre[:30]:<30} {ciudad[:20]:<20} {provincia[:15]:<15} {hoyos:<6} {par:<4} {num_rec:<5} {num_barras:<7} {num_hoyos:<6}")
    
    conn.close()

if __name__ == "__main__":
    # Importar todos los campos disponibles
    importar_todos_campos()
    
    # Mostrar un resumen de los campos importados
    mostrar_campos_importados()
