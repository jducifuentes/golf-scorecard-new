import json
import os
from descargar_paginas_campos import descargar_paginas_campos

def descargar_campos_especificos(ids_campos):
    """
    Descarga solo los campos con los IDs especificados
    """
    # Ruta al archivo JSON de campos de golf
    archivo_json = "output/campos_golf.json"
    
    # Directorio donde se guardarán las páginas HTML
    directorio_salida = "output/paginas_campos"
    
    # Verificar que el archivo JSON existe
    if not os.path.exists(archivo_json):
        print(f"El archivo {archivo_json} no existe.")
        return
    
    # Cargar el archivo JSON
    with open(archivo_json, 'r', encoding='utf-8') as f:
        todos_los_campos = json.load(f)
    
    # Filtrar solo los campos que queremos descargar
    campos_a_descargar = [campo for campo in todos_los_campos if str(campo.get('id')) in ids_campos]
    
    if not campos_a_descargar:
        print("No se encontraron campos con los IDs especificados.")
        return
    
    print(f"Se van a descargar {len(campos_a_descargar)} campos:")
    for campo in campos_a_descargar:
        print(f"  - {campo.get('nombre', 'Desconocido')} (ID: {campo.get('id')})")
    
    # Crear un archivo JSON temporal con solo los campos que queremos descargar
    archivo_json_temp = "output/campos_faltantes.json"
    with open(archivo_json_temp, 'w', encoding='utf-8') as f:
        json.dump(campos_a_descargar, f, ensure_ascii=False, indent=2)
    
    # Descargar los campos
    descargar_paginas_campos(archivo_json_temp, directorio_salida)
    
    # Eliminar el archivo JSON temporal
    os.remove(archivo_json_temp)
    print("Proceso completado.")

if __name__ == "__main__":
    # IDs de los campos que fallaron en la descarga anterior
    campos_faltantes = [
        "983",  # EL VALLE
        "518",  # EMPORDA
        "332",  # ENTREPINOS
        "481",  # ESC LA CARTUJA
        "563",  # LAS REJAS
        "913"   # LAUKARIZ
    ]
    
    descargar_campos_especificos(campos_faltantes)
