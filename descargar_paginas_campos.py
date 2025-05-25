import requests
import json
import os
import time
import logging
import re
from datetime import datetime
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup

def extraer_opciones_recorridos_y_sexos(html_content):
    """
    Extrae las opciones de recorridos y sexos disponibles en la página HTML
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Buscar opciones de recorridos
    recorridos = []
    recorrido_select_id = None
    
    selects = soup.find_all('select')
    for select in selects:
        options = select.find_all('option')
        # Verificar si este select parece contener recorridos
        es_selector_recorridos = False
        for option in options:
            option_text = option.text.strip()
            # Buscar patrones comunes en nombres de recorridos: "Course", "campo", "recorrido", etc.
            if "Course" in option_text or "course" in option_text or "Campo" in option_text or "Recorrido" in option_text:
                es_selector_recorridos = True
                break
        
        # Si parece ser un selector de recorridos, extraer todas las opciones
        if es_selector_recorridos:
            recorrido_select_id = select.get('id', '')
            for option in options:
                recorridos.append({
                    'id': option.get('value'),
                    'nombre': option.text.strip()
                })
            break  # Solo procesamos el primer selector que parece contener recorridos
    
    # Buscar opciones de sexo
    sexos = []
    sexo_select_id = None
    
    for select in selects:
        options = select.find_all('option')
        # Verificar si este select parece contener opciones de sexo
        es_selector_sexo = False
        for option in options:
            option_text = option.text.strip().lower()
            if "masculino" in option_text or "femenino" in option_text or "hombre" in option_text or "mujer" in option_text:
                es_selector_sexo = True
                break
        
        # Si parece ser un selector de sexo, extraer todas las opciones
        if es_selector_sexo:
            sexo_select_id = select.get('id', '')
            for option in options:
                sexos.append({
                    'id': option.get('value'),
                    'nombre': option.text.strip()
                })
            break  # Solo procesamos el primer selector que parece contener opciones de sexo
    
    # Si no se encontraron recorridos, añadir uno por defecto
    if not recorridos:
        recorridos = [{'id': '0', 'nombre': 'Recorrido Principal'}]
    
    # Si no se encontraron opciones de sexo, añadir una por defecto
    if not sexos:
        sexos = [{'id': '0', 'nombre': 'Masculino'}]
    
    return recorridos, sexos, recorrido_select_id, sexo_select_id

def extraer_datos_formulario(html_content):
    """
    Extrae los datos necesarios para hacer un postback
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extraer el viewstate
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})
    viewstate_value = viewstate.get('value', '') if viewstate else ''
    
    # Extraer el eventvalidation
    eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
    eventvalidation_value = eventvalidation.get('value', '') if eventvalidation else ''
    
    # Extraer el viewstategenerator
    viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
    viewstategenerator_value = viewstategenerator.get('value', '') if viewstategenerator else ''
    
    return {
        '__VIEWSTATE': viewstate_value,
        '__EVENTVALIDATION': eventvalidation_value,
        '__VIEWSTATEGENERATOR': viewstategenerator_value
    }

def simular_postback(url, target, event_argument, form_data, headers, timeout=10):
    """
    Simula un postback de ASP.NET
    """
    # Añadir los datos específicos del postback
    form_data['__EVENTTARGET'] = target
    form_data['__EVENTARGUMENT'] = event_argument
    
    # Realizar la petición POST
    response = requests.post(url, data=form_data, headers=headers, timeout=timeout)
    response.raise_for_status()
    
    return response.text

def normalizar_nombre_archivo(texto):
    """
    Normaliza un texto para usarlo como nombre de archivo
    """
    # Eliminar caracteres no permitidos en nombres de archivo
    texto = re.sub(r'[<>:"/\\|?*]', '', texto)
    # Reemplazar espacios y otros caracteres por guiones bajos
    texto = re.sub(r'[\s\-]+', '_', texto)
    # Convertir a minúsculas
    texto = texto.lower()
    # Eliminar acentos y caracteres especiales
    texto = texto.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    texto = texto.replace('ñ', 'n').replace('ü', 'u')
    # Limitar longitud
    texto = texto[:50]
    return texto

def extraer_nombre_campo(html_content):
    """
    Extrae el nombre del campo de golf desde el HTML
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Intentar extraer el nombre del campo
    nombre_campo = "campo_desconocido"
    div_club_name = soup.find('div', id=re.compile('dvClubName'))
    if div_club_name:
        nombre_campo = div_club_name.text.strip()
    
    return nombre_campo

def descargar_pagina_campo(url, campo_id, nombre_campo, directorio_salida, headers, logger, progreso_file):
    """
    Descarga la página principal del campo y luego todas las combinaciones de recorridos y sexos
    """
    # Intentar descargar la página principal
    max_intentos = 3
    intentos = 0
    html_content = None
    
    while intentos < max_intentos:
        try:
            tiempo_inicio = time.time()
            response = requests.get(url, headers=headers, timeout=10)
            tiempo_fin = time.time()
            response.raise_for_status()  # Lanzar excepción si hay error HTTP
            
            html_content = response.text
            
            # Extraer el nombre real del campo desde el HTML
            nombre_campo_real = extraer_nombre_campo(html_content)
            nombre_campo_normalizado = normalizar_nombre_archivo(nombre_campo_real)
            
            # Nombre del archivo principal
            nombre_archivo_principal = f"campo_{campo_id}_{nombre_campo_normalizado}.html"
            ruta_archivo_principal = os.path.join(directorio_salida, nombre_archivo_principal)
            
            # Guardar la página principal
            with open(ruta_archivo_principal, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            mensaje = f"Página principal guardada en: {ruta_archivo_principal} (Tiempo: {tiempo_fin - tiempo_inicio:.2f}s)"
            logger.info(mensaje)
            with open(progreso_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().strftime('%H:%M:%S')} - Campo {campo_id} ({nombre_campo_real}): Descargado correctamente\n")
            break
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            intentos += 1
            mensaje = f"Error al descargar la página principal ({intentos}/{max_intentos}): {e}"
            logger.error(mensaje)
            if intentos < max_intentos:
                tiempo_espera = 1
                logger.info(f"Reintentando en {tiempo_espera} segundos...")
                time.sleep(tiempo_espera)
            else:
                mensaje = f"No se pudo descargar la página principal después de {max_intentos} intentos."
                logger.error(mensaje)
                with open(progreso_file, 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now().strftime('%H:%M:%S')} - Campo {campo_id} ({nombre_campo}): ERROR - {e}\n")
                return False
    
    if not html_content:
        return False
    
    # Extraer opciones de recorridos y sexos
    recorridos, sexos, recorrido_select_id, sexo_select_id = extraer_opciones_recorridos_y_sexos(html_content)
    
    logger.info(f"Recorridos encontrados: {len(recorridos)}")
    for rec in recorridos:
        logger.info(f"  - {rec['nombre']} (ID: {rec['id']})")
    
    logger.info(f"Opciones de sexo encontradas: {len(sexos)}")
    for sexo in sexos:
        logger.info(f"  - {sexo['nombre']} (ID: {sexo['id']})")
    
    # Si solo hay un recorrido y un sexo, ya tenemos la página principal
    if len(recorridos) == 1 and len(sexos) == 1 and recorridos[0]['id'] == '0' and sexos[0]['id'] == '0':
        logger.info("No se encontraron múltiples recorridos ni opciones de sexo. Solo se guardará la página principal.")
        return True
    
    # Extraer datos del formulario para hacer postbacks
    form_data = extraer_datos_formulario(html_content)
    
    # Descargar cada combinación de recorrido y sexo
    for recorrido in recorridos:
        for sexo in sexos:
            # Si ambos son los valores por defecto, ya tenemos la página principal
            if recorrido['id'] == '0' and sexo['id'] == '0':
                continue
            
            # Normalizar nombres para el archivo
            nombre_recorrido_normalizado = normalizar_nombre_archivo(recorrido['nombre'])
            nombre_sexo_normalizado = normalizar_nombre_archivo(sexo['nombre'])
            
            # Nombre del archivo para esta combinación
            nombre_archivo = f"campo_{campo_id}_{nombre_campo_normalizado}_recorrido_{recorrido['id']}_{nombre_recorrido_normalizado}_sexo_{sexo['id']}_{nombre_sexo_normalizado}.html"
            ruta_archivo = os.path.join(directorio_salida, nombre_archivo)
            
            # Verificar si el archivo ya existe
            if os.path.exists(ruta_archivo):
                mensaje = f"El archivo {nombre_archivo} ya existe. Omitiendo descarga."
                logger.info(mensaje)
                continue
            
            # Intentar descargar esta combinación específica
            mensaje = f"Descargando: Recorrido '{recorrido['nombre']}' (ID: {recorrido['id']}), Sexo '{sexo['nombre']}' (ID: {sexo['id']})"
            logger.info(mensaje)
            
            try:
                # Primero cambiamos el recorrido si es necesario
                if recorrido['id'] != '0' and recorrido_select_id:
                    # Clonar los datos del formulario para no modificar el original
                    form_data_recorrido = form_data.copy()
                    
                    # Añadir el valor seleccionado
                    form_data_recorrido[recorrido_select_id] = recorrido['id']
                    
                    # Simular el postback para cambiar el recorrido
                    html_content = simular_postback(url, recorrido_select_id, '', form_data_recorrido, headers)
                    
                    # Actualizar los datos del formulario con los nuevos valores
                    form_data = extraer_datos_formulario(html_content)
                
                # Luego cambiamos el sexo si es necesario
                if sexo['id'] != '0' and sexo_select_id:
                    # Clonar los datos del formulario para no modificar el original
                    form_data_sexo = form_data.copy()
                    
                    # Añadir el valor seleccionado
                    form_data_sexo[sexo_select_id] = sexo['id']
                    
                    # Simular el postback para cambiar el sexo
                    html_content = simular_postback(url, sexo_select_id, '', form_data_sexo, headers)
                
                # Guardar el HTML resultante
                with open(ruta_archivo, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                mensaje = f"Combinación guardada en: {ruta_archivo}"
                logger.info(mensaje)
            except Exception as e:
                mensaje = f"Error al descargar la combinación: {e}"
                logger.error(mensaje)
            
            # Esperar un tiempo entre descargas
            time.sleep(1)
    
    return True

def descargar_paginas_campos(archivo_json, directorio_salida):
    """
    Recorre el archivo JSON de campos de golf y descarga la página HTML de cada campo
    guardándola en el directorio de salida especificado.
    """
    # Configurar logging
    os.makedirs('logs', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f'logs/descarga_campos_{timestamp}.log'
    
    # Configurar logger
    logger = logging.getLogger('descarga_campos')
    logger.setLevel(logging.INFO)
    
    # Handler para archivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formato del log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Añadir handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Crear directorio de salida si no existe
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Cargar el archivo JSON
    logger.info(f"Cargando archivo JSON: {archivo_json}")
    with open(archivo_json, 'r', encoding='utf-8') as f:
        campos = json.load(f)
    
    logger.info(f"Se encontraron {len(campos)} campos de golf")
    
    # Crear archivo de progreso
    progreso_file = f'logs/progreso_descarga_{timestamp}.txt'
    with open(progreso_file, 'w', encoding='utf-8') as f:
        f.write(f"Inicio de descarga: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total de campos: {len(campos)}\n\n")
    
    # Headers para simular un navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    # Estadísticas
    exitos = 0
    fallos = 0
    omitidos = 0
    
    # Recorrer cada campo y descargar su página
    for i, campo in enumerate(campos, 1):
        campo_id = campo.get('id')
        nombre_campo = campo.get('nombre', 'desconocido')
        url = campo.get('url', '')
        
        # Corregir URL
        if url:
            # Asegurarse de que la URL tenga el formato correcto
            if 'rfegolf.es' in url and 'ClubPaginas' in url:
                # Corregir el formato: asegurarse de que hay un slash entre rfegolf.es y ClubPaginas
                url = url.replace('rfegolf.esClubPaginas', 'rfegolf.es/ClubPaginas')
            
            # Añadir https:// si falta
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url.replace('https://', '').replace('http://', '')
        
        if not url:
            mensaje = f"[{i}/{len(campos)}] Error: URL vacía para el campo {nombre_campo} (ID: {campo_id})"
            logger.error(mensaje)
            with open(progreso_file, 'a', encoding='utf-8') as f:
                f.write(f"{mensaje}\n")
            fallos += 1
            continue
        
        mensaje = f"[{i}/{len(campos)}] Procesando campo: {nombre_campo} (ID: {campo_id})"
        logger.info(mensaje)
        logger.info(f"URL: {url}")
        
        # Normalizar el nombre del campo para el archivo
        nombre_campo_normalizado = normalizar_nombre_archivo(nombre_campo)
        
        # Nombre del archivo principal
        nombre_archivo = f"campo_{campo_id}_{nombre_campo_normalizado}.html"
        ruta_archivo = os.path.join(directorio_salida, nombre_archivo)
        
        # Verificar si el archivo ya existe y si queremos sobrescribirlo
        if os.path.exists(ruta_archivo):
            mensaje = f"El archivo {nombre_archivo} ya existe."
            logger.info(mensaje)
            
            # Aquí podrías decidir si quieres sobrescribir o no
            # Por ahora, vamos a sobrescribir para asegurarnos de tener datos actualizados
            logger.info("Se descargará de nuevo para obtener datos actualizados.")
        
        # Descargar la página principal y todas las combinaciones
        if descargar_pagina_campo(url, campo_id, nombre_campo, directorio_salida, headers, logger, progreso_file):
            exitos += 1
        else:
            fallos += 1
        
        # Esperar un tiempo mínimo entre campos
        if i < len(campos):
            time.sleep(0.5)
    
    # Resumen final
    mensaje_final = f"\nProceso completado. Total: {len(campos)}, Éxitos: {exitos}, Fallos: {fallos}, Omitidos: {omitidos}"
    logger.info(mensaje_final)
    with open(progreso_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{mensaje_final}\n")
        f.write(f"Fin de descarga: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def main():
    # Ruta al archivo JSON de campos de golf
    archivo_json = "output/campos_golf.json"
    
    # Directorio donde se guardarán las páginas HTML
    directorio_salida = "output/paginas_campos"
    
    # Descargar las páginas
    descargar_paginas_campos(archivo_json, directorio_salida)

if __name__ == "__main__":
    main()
