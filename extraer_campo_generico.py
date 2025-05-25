import os
import re
import sys
import glob
from bs4 import BeautifulSoup

def extraer_informacion_recorrido(soup, nombre_recorrido="Recorrido Principal", sexo="Masculino"):
    """
    Extrae la información de un recorrido específico desde el objeto BeautifulSoup
    """
    # Buscar tablas que puedan contener información de barras
    tablas = soup.find_all('table', class_=re.compile('grid_GridOlympus'))
    
    barras = []
    
    if tablas:
        print(f"\nSe encontraron {len(tablas)} tablas de barras para el recorrido: {nombre_recorrido} (Sexo: {sexo})")
        
        for i, tabla in enumerate(tablas, 1):
            print(f"\nTabla {i}:")
            
            # Extraer filas de la tabla
            filas = tabla.find_all('tr')
            
            if len(filas) >= 3:  # Verificar que hay suficientes filas (cabecera, metros, par, handicap)
                # Obtener el nombre de la barra de la primera fila
                primera_fila = filas[0]
                celdas_primera_fila = primera_fila.find_all(['th'])
                
                if len(celdas_primera_fila) > 1:
                    nombre_barra = celdas_primera_fila[1].text.strip()
                    print(f"Barra: {nombre_barra}")
                    
                    # Extraer datos de metros, par y handicap
                    metros_row = [celda.text.strip() for celda in filas[1].find_all(['td'])]
                    par_row = [celda.text.strip() for celda in filas[2].find_all(['td'])]
                    
                    if len(metros_row) > 0 and len(par_row) > 0:
                        # Extraer valoración y slope total
                        valoracion_total = None
                        slope_total = None
                        
                        # Buscar los valores de VC y VS en la fila de par
                        if len(par_row) >= 29:  # Asegurarse de que hay suficientes columnas
                            try:
                                # Mostrar todos los valores para depuración
                                print(f"  Valores en la fila par: {par_row[-5:]}") # Mostrar los últimos 5 valores
                                
                                # El par total está en el índice -4, VC en -3, y VS en -2
                                # Verificar si el texto es un número válido
                                if par_row[-3] and par_row[-3].replace('.', '', 1).replace(',', '', 1).isdigit():
                                    valoracion_total = float(par_row[-3].replace(',', '.'))
                                
                                if par_row[-2] and par_row[-2].replace('.', '', 1).replace(',', '', 1).isdigit():
                                    slope_total = float(par_row[-2].replace(',', '.'))
                                
                                print(f"  Valores extraídos - VC: {valoracion_total}, VS: {slope_total}")
                            except (ValueError, IndexError) as e:
                                print(f"Error al extraer VC/VS para {nombre_barra}: {e}")
                                pass
                        
                        # Crear estructura de hoyos
                        hoyos = []
                        metros_totales = 0
                        par_total = 0
                        
                        # Procesar hoyos del 1 al 9
                        for h in range(1, 10):
                            idx = h + 1  # Ajustar índice para los hoyos
                            
                            if idx < len(metros_row) and idx < len(par_row):
                                try:
                                    metros = int(metros_row[idx]) if metros_row[idx].isdigit() else 0
                                    par = int(par_row[idx]) if par_row[idx].isdigit() else 0
                                    
                                    # Para el handicap, necesitamos la tercera fila si existe
                                    hcp = 0
                                    if len(filas) > 3:
                                        hcp_row = [celda.text.strip() for celda in filas[3].find_all(['td'])]
                                        if idx < len(hcp_row) and hcp_row[idx].isdigit():
                                            hcp = int(hcp_row[idx])
                                    
                                    hoyo = {
                                        "numero": h,
                                        "metros": metros,
                                        "par": par,
                                        "hcp": hcp
                                    }
                                    
                                    hoyos.append(hoyo)
                                    metros_totales += metros
                                    par_total += par
                                except (ValueError, IndexError):
                                    pass
                        
                        # Procesar hoyos del 10 al 18
                        for h in range(10, 19):
                            idx = h + 4  # Ajustar índice para los hoyos de la vuelta
                            
                            if idx < len(metros_row) and idx < len(par_row):
                                try:
                                    metros = int(metros_row[idx]) if metros_row[idx].isdigit() else 0
                                    par = int(par_row[idx]) if par_row[idx].isdigit() else 0
                                    
                                    # Para el handicap, necesitamos la tercera fila si existe
                                    hcp = 0
                                    if len(filas) > 3:
                                        hcp_row = [celda.text.strip() for celda in filas[3].find_all(['td'])]
                                        if idx < len(hcp_row) and hcp_row[idx].isdigit():
                                            hcp = int(hcp_row[idx])
                                    
                                    hoyo = {
                                        "numero": h,
                                        "metros": metros,
                                        "par": par,
                                        "hcp": hcp
                                    }
                                    
                                    hoyos.append(hoyo)
                                    metros_totales += metros
                                    par_total += par
                                except (ValueError, IndexError):
                                    pass
                        
                        # Crear barra
                        if hoyos:
                            barra = {
                                "nombre": nombre_barra,
                                "valor_campo": valoracion_total,
                                "slope": slope_total,
                                "metros_totales": metros_totales,
                                "par_total": par_total,
                                "sexo": sexo,
                                "hoyos": hoyos
                            }
                            
                            barras.append(barra)
                            
                            print(f"Barra {nombre_barra}: {metros_totales} metros, Par {par_total}")
                            if valoracion_total:
                                print(f"  Valoración total: {valoracion_total}")
                            if slope_total:
                                print(f"  Slope total: {slope_total}")
            else:
                print("No hay suficientes filas en la tabla para extraer información completa")
    else:
        print("No se encontraron tablas de barras")
    
    return barras

def extraer_informacion_campo(archivo_html):
    """
    Extrae la información del campo de golf desde el archivo HTML
    """
    print(f"Procesando archivo: {archivo_html}")
    
    # Verificar si el archivo existe
    if not os.path.exists(archivo_html):
        print(f"El archivo {archivo_html} no existe.")
        return None
    
    # Leer el archivo HTML
    with open(archivo_html, 'r', encoding='utf-8') as f:
        contenido_html = f.read()
    
    # Crear objeto BeautifulSoup
    soup = BeautifulSoup(contenido_html, 'html.parser')
    
    # Extraer información básica del campo
    info_campo = {}
    
    # Intentar extraer el nombre del campo
    nombre_campo = "Campo Desconocido"
    div_club_name = soup.find('div', id=re.compile('dvClubName'))
    if div_club_name:
        nombre_campo = div_club_name.text.strip()
    info_campo['nombre'] = nombre_campo
    print(f"Nombre del campo: {info_campo['nombre']}")
    
    # Buscar opciones de recorridos disponibles
    recorridos_disponibles = []
    
    # Buscar el selector que contiene los recorridos (buscar por patrones comunes en los selectores de recorridos)
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
            for option in options:
                recorridos_disponibles.append({
                    'id': option.get('value'),
                    'nombre': option.text.strip()
                })
            break  # Solo procesamos el primer selector que parece contener recorridos
    
    if recorridos_disponibles:
        print(f"Recorridos disponibles: {len(recorridos_disponibles)}")
        for rec in recorridos_disponibles:
            print(f"  - {rec['nombre']} (ID: {rec['id']})")
    else:
        # Si no encontramos recorridos específicos, asumimos que hay un solo recorrido
        recorridos_disponibles = [{'id': '0', 'nombre': 'Recorrido Principal'}]
        print("No se encontraron múltiples recorridos, asumiendo recorrido único")
    
    # Buscar opciones de sexo disponibles
    sexos_disponibles = []
    
    # Buscar el selector que contiene los sexos
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
            for option in options:
                sexos_disponibles.append({
                    'id': option.get('value'),
                    'nombre': option.text.strip()
                })
            break  # Solo procesamos el primer selector que parece contener opciones de sexo
    
    if sexos_disponibles:
        print(f"Sexos disponibles: {len(sexos_disponibles)}")
        for sexo in sexos_disponibles:
            print(f"  - {sexo['nombre']} (ID: {sexo['id']})")
    else:
        # Si no encontramos sexos específicos, asumimos que es masculino
        sexos_disponibles = [{'id': '0', 'nombre': 'Masculino'}]
        print("No se encontraron múltiples opciones de sexo, asumiendo masculino")
    
    # Procesar cada recorrido
    recorridos = []
    
    # Extraer información del primer recorrido (el que ya está cargado en la página)
    barras_primer_recorrido = extraer_informacion_recorrido(soup, recorridos_disponibles[0]['nombre'], sexos_disponibles[0]['nombre'])
    
    if barras_primer_recorrido:
        recorridos.append({
            'nombre': recorridos_disponibles[0]['nombre'],
            'id': recorridos_disponibles[0]['id'],
            'sexo': sexos_disponibles[0]['nombre'],
            'sexo_id': sexos_disponibles[0]['id'],
            'barras': barras_primer_recorrido
        })
    
    # Agregar recorridos a la información del campo
    if recorridos:
        info_campo['recorridos'] = recorridos
    
    return info_campo

def procesar_archivos_campo(id_campo):
    """
    Procesa todos los archivos HTML relacionados con un campo específico
    """
    # Ruta al directorio de archivos HTML
    directorio_html = "output/paginas_campos"
    
    # Buscar el archivo principal del campo (ahora incluye el nombre del campo en el nombre del archivo)
    patron_archivo_principal = f"{directorio_html}/campo_{id_campo}_*.html"
    archivos_principales = glob.glob(patron_archivo_principal)
    
    # Filtrar para obtener solo el archivo principal (sin recorrido ni sexo en el nombre)
    archivo_principal = None
    for archivo in archivos_principales:
        if "recorrido_" not in archivo and "sexo_" not in archivo:
            archivo_principal = archivo
            break
    
    # Si no se encuentra el archivo principal, intentar con el formato antiguo
    if not archivo_principal:
        archivo_principal = f"{directorio_html}/campo_{id_campo}.html"
    
    # Verificar si el archivo principal existe
    if not os.path.exists(archivo_principal):
        print(f"El archivo principal para el campo {id_campo} no existe.")
        return None
    
    print(f"Usando archivo principal: {archivo_principal}")
    
    # Extraer información básica del campo desde el archivo principal
    info_campo = extraer_informacion_campo(archivo_principal)
    
    if not info_campo:
        print("No se pudo extraer información del campo.")
        return None
    
    # Buscar todos los archivos adicionales para este campo
    patron_archivos = f"{directorio_html}/campo_{id_campo}_*recorrido_*_*sexo_*.html"
    archivos_adicionales = glob.glob(patron_archivos)
    
    print(f"\nSe encontraron {len(archivos_adicionales)} archivos adicionales para el campo {id_campo}")
    
    # Procesar cada archivo adicional
    for archivo in archivos_adicionales:
        print(f"\nProcesando archivo adicional: {archivo}")
        
        # Extraer IDs de recorrido y sexo del nombre del archivo
        match_recorrido = re.search(r"recorrido_(\d+)_", archivo)
        match_sexo = re.search(r"sexo_(\d+)_", archivo)
        
        # Si no se encuentra con el nuevo formato, intentar con el formato antiguo
        if not match_recorrido:
            match_recorrido = re.search(r"recorrido_(\d+)\.", archivo)
        if not match_sexo:
            match_sexo = re.search(r"sexo_(\d+)\.", archivo)
        
        if match_recorrido and match_sexo:
            id_recorrido = match_recorrido.group(1)
            id_sexo = match_sexo.group(1)
            
            print(f"ID de recorrido: {id_recorrido}, ID de sexo: {id_sexo}")
            
            # Extraer nombres de recorrido y sexo del nombre del archivo
            nombre_recorrido_match = re.search(r"recorrido_\d+_([^_]+)_sexo", archivo)
            nombre_sexo_match = re.search(r"sexo_\d+_([^\.]+)", archivo)
            
            nombre_recorrido = f"Recorrido {id_recorrido}"
            nombre_sexo = f"Sexo {id_sexo}"
            
            # Si se encuentran los nombres en el archivo, usarlos
            if nombre_recorrido_match:
                nombre_recorrido = nombre_recorrido_match.group(1).replace('_', ' ')
            if nombre_sexo_match:
                nombre_sexo = nombre_sexo_match.group(1).replace('_', ' ')
            
            # Leer el archivo HTML
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido_html = f.read()
            
            # Crear objeto BeautifulSoup
            soup = BeautifulSoup(contenido_html, 'html.parser')
            
            # Intentar encontrar el nombre real del recorrido y sexo en el HTML si no se encontró en el nombre del archivo
            if nombre_recorrido == f"Recorrido {id_recorrido}" or nombre_sexo == f"Sexo {id_sexo}":
                selects = soup.find_all('select')
                for select in selects:
                    options = select.find_all('option', {'value': id_recorrido})
                    if options:
                        nombre_recorrido = options[0].text.strip()
                        break
                
                for select in selects:
                    options = select.find_all('option', {'value': id_sexo})
                    if options:
                        nombre_sexo = options[0].text.strip()
                        break
            
            # Extraer información del recorrido adicional
            barras_recorrido = extraer_informacion_recorrido(soup, nombre_recorrido, nombre_sexo)
            
            if barras_recorrido and 'recorridos' in info_campo:
                # Verificar si ya existe este recorrido con este sexo
                recorrido_existente = False
                for recorrido in info_campo['recorridos']:
                    if recorrido['id'] == id_recorrido and recorrido['sexo_id'] == id_sexo:
                        recorrido_existente = True
                        break
                
                if not recorrido_existente:
                    # Añadir este recorrido a la información del campo
                    info_campo['recorridos'].append({
                        'nombre': nombre_recorrido,
                        'id': id_recorrido,
                        'sexo': nombre_sexo,
                        'sexo_id': id_sexo,
                        'barras': barras_recorrido
                    })
    
    return info_campo

def main():
    # Verificar si se proporcionó un ID de campo como argumento
    if len(sys.argv) < 2:
        print("Uso: python extraer_campo_generico.py <id_campo> [id_recorrido] [id_sexo]")
        return
    
    # Obtener el ID del campo desde los argumentos
    id_campo = sys.argv[1]
    
    # Procesar todos los archivos relacionados con este campo
    info_campo = procesar_archivos_campo(id_campo)
    
    # Si se proporcionaron IDs específicos de recorrido y sexo, filtrar los resultados
    if len(sys.argv) > 2:
        id_recorrido = sys.argv[2]
        id_sexo = sys.argv[3] if len(sys.argv) > 3 else None
        
        if info_campo and 'recorridos' in info_campo:
            recorridos_filtrados = []
            
            for recorrido in info_campo['recorridos']:
                if recorrido['id'] == id_recorrido:
                    if id_sexo is None or recorrido['sexo_id'] == id_sexo:
                        recorridos_filtrados.append(recorrido)
            
            if recorridos_filtrados:
                info_campo['recorridos'] = recorridos_filtrados
            else:
                print(f"No se encontró información para el recorrido {id_recorrido} y sexo {id_sexo}")
    
    if info_campo:
        print("\nResumen de la información extraída:")
        for clave, valor in info_campo.items():
            if clave != 'recorridos':
                print(f"{clave}: {valor}")
        
        if 'recorridos' in info_campo:
            print(f"\nRecorridos encontrados: {len(info_campo['recorridos'])}")
            for i, recorrido in enumerate(info_campo['recorridos'], 1):
                print(f"\nRecorrido {i}: {recorrido['nombre']} (Sexo: {recorrido['sexo']})")
                
                if 'barras' in recorrido:
                    print(f"  Barras encontradas: {len(recorrido['barras'])}")
                    for j, barra in enumerate(recorrido['barras'], 1):
                        print(f"  Barra {j}: {barra['nombre']}")
                        print(f"    Valoración: {barra.get('valor_campo', 'No disponible')}")
                        print(f"    Slope: {barra.get('slope', 'No disponible')}")
                        print(f"    Metros totales: {barra.get('metros_totales', 0)}")
                        print(f"    Par total: {barra.get('par_total', 0)}")

if __name__ == "__main__":
    main()
