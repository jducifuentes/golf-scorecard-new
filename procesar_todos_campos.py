import json
import os
import time
import random
import logging
from datetime import datetime
from extractor_campo import extraer_informacion_campo

# Configurar el sistema de logging
def configurar_logging():
    # Crear directorio de logs si no existe
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar el logger principal
    logger = logging.getLogger('procesar_campos')
    logger.setLevel(logging.INFO)
    
    # Crear un formateador para los logs
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Crear un manejador para el archivo de log general
    fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'procesar_campos_{fecha_actual}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Crear un manejador para el archivo de log de errores
    error_log_file = os.path.join(log_dir, f'procesar_campos_errores_{fecha_actual}.log')
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

def procesar_campos_golf(archivo_campos, directorio_salida="output/campos", limite=None, inicio=0):
    """
    Procesa todos los campos de golf del archivo JSON y extrae su información detallada.
    
    Args:
        archivo_campos (str): Ruta al archivo JSON con la lista de campos.
        directorio_salida (str): Directorio donde se guardarán los archivos JSON de cada campo.
        limite (int, optional): Número máximo de campos a procesar. None para procesar todos.
        inicio (int, optional): Índice del primer campo a procesar. Por defecto 0.
    """
    # Configurar el sistema de logging
    logger = configurar_logging()
    
    # Cargar la lista de campos
    try:
        with open(archivo_campos, 'r', encoding='utf-8') as f:
            campos = json.load(f)
    except Exception as e:
        logger.error(f"Error al cargar el archivo de campos: {e}")
        return
    
    logger.info(f"Total de campos: {len(campos)}")
    
    # Crear el directorio de salida si no existe
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)
    
    # Determinar cuántos campos procesar
    total_campos = len(campos)
    if limite:
        campos_a_procesar = min(limite, total_campos - inicio)
        logger.info(f"Procesando {campos_a_procesar} campos a partir del índice {inicio}")
    else:
        campos_a_procesar = total_campos - inicio
        logger.info(f"Procesando todos los campos ({campos_a_procesar}) a partir del índice {inicio}")
    
    # Procesar cada campo
    for i, campo in enumerate(campos[inicio:inicio + campos_a_procesar], 1):
        id_campo = campo.get('id')
        nombre = campo.get('nombre')
        url = campo.get('url')
        
        # Corregir la URL si es necesario
        if url and "rfegolf.es" in url:
            url = url.replace("rfegolf.esClubPaginas", "rfegolf.es/ClubPaginas")
        
        logger.info(f"[{i}/{campos_a_procesar}] Procesando campo: {nombre} (ID: {id_campo})")
        
        # Nombre del archivo de salida
        archivo_salida = os.path.join(directorio_salida, f"campo_{id_campo}.json")
        
        # Verificar si el archivo ya existe
        if os.path.exists(archivo_salida):
            logger.info(f"  El archivo {archivo_salida} ya existe. Omitiendo...")
            continue
        
        # Extraer información del campo
        try:
            logger.info(f"Extrayendo información del campo: {url}")
            info_campo = extraer_informacion_campo(url)
            
            # Guardar la información en un archivo JSON
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(info_campo, f, ensure_ascii=False, indent=2)
            
            logger.info(f"  Información guardada en {archivo_salida}")
            
            # Esperar un tiempo aleatorio para no sobrecargar el servidor
            tiempo_espera = random.uniform(1, 3)
            logger.info(f"  Esperando {tiempo_espera:.2f} segundos...")
            time.sleep(tiempo_espera)
            
        except Exception as e:
            logger.error(f"Error al procesar el campo {nombre} (ID: {id_campo}): {e}", exc_info=True)
            
            # Guardar un archivo JSON vacío con la información básica
            info_basica = {
                "url": url,
                "id": id_campo,
                "error": str(e),
                "recorridos": []
            }
            
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(info_basica, f, ensure_ascii=False, indent=2)
            
            logger.info(f"  Se guardó información básica en {archivo_salida} debido a un error")
    
    logger.info("Proceso completado.")

if __name__ == "__main__":
    # Archivo con la lista de campos
    archivo_campos = "output/campos_golf.json"
    
    # Procesar todos los campos
    # Cambiar limite a un número específico para procesar solo algunos campos
    procesar_campos_golf(archivo_campos, limite=None)
