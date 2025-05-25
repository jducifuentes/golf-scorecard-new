import os
import re
from bs4 import BeautifulSoup

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
    
    # Nombre del campo
    nombre_campo = soup.find('span', id=lambda x: x and 'Label1' in x)
    if nombre_campo:
        info_campo['nombre'] = nombre_campo.text.strip()
    else:
        # Buscar de otra manera
        titulo = soup.find('title')
        if titulo:
            info_campo['nombre'] = titulo.text.strip()
        else:
            info_campo['nombre'] = "Nombre no encontrado"
    
    print(f"Nombre del campo: {info_campo.get('nombre', 'No encontrado')}")
    
    # Dirección y ubicación
    direccion = soup.find(text=re.compile('CALLE'))
    if direccion:
        info_campo['direccion'] = direccion.strip()
        print(f"Dirección: {info_campo.get('direccion', 'No encontrada')}")
    
    # Buscar información de provincia
    provincia = soup.find(text=re.compile('LEON'))
    if provincia:
        info_campo['provincia'] = provincia.strip()
        print(f"Provincia: {info_campo.get('provincia', 'No encontrada')}")
    
    # Buscar tablas que puedan contener información de recorridos
    tablas = soup.find_all('table', class_=re.compile('grid_GridOlympus'))
    
    if tablas:
        print(f"Se encontraron {len(tablas)} tablas de recorridos")
        
        for i, tabla in enumerate(tablas, 1):
            print(f"\nTabla {i}:")
            
            # Intentar extraer filas
            filas = tabla.find_all('tr')
            if filas:
                print(f"La tabla tiene {len(filas)} filas")
                
                for j, fila in enumerate(filas):
                    celdas = fila.find_all(['th', 'td'])
                    if celdas:
                        contenido_fila = [celda.text.strip() for celda in celdas]
                        print(f"  Fila {j}: {' | '.join(contenido_fila)}")
            else:
                print("No se encontraron filas en la tabla")
    else:
        print("No se encontraron tablas de recorridos")
    
    # Buscar información sobre barras, slope y valoración
    barras_info = []
    
    # Buscar elementos que puedan contener información de barras
    elementos_barras = soup.find_all(['div', 'span', 'td'], text=re.compile('(NEGRAS|BLANCAS|AMARILLAS|ROJAS|AZULES|VERDES)'))
    
    if elementos_barras:
        print("\nInformación de barras encontrada:")
        for elem in elementos_barras:
            print(f"  {elem.text.strip()}")
            
            # Intentar encontrar información de slope y valoración cerca de este elemento
            padre = elem.parent
            if padre:
                hermanos = padre.find_all(['div', 'span', 'td'])
                for hermano in hermanos:
                    texto = hermano.text.strip()
                    if re.search(r'\d+\.\d+', texto) or re.search(r'\b\d{2,3}\b', texto):
                        print(f"    Posible Slope/Valoración: {texto}")
    else:
        print("\nNo se encontró información de barras")
    
    # Buscar elementos que contengan "Slope" o "Valoración"
    elementos_slope = soup.find_all(text=re.compile('(Slope|Valoraci[oó]n|Vc|Vs)'))
    if elementos_slope:
        print("\nReferencias a Slope o Valoración:")
        for elem in elementos_slope:
            print(f"  {elem.strip()}")
            
            # Buscar números cercanos
            padre = elem.parent
            if padre:
                texto_completo = padre.text.strip()
                numeros = re.findall(r'\b\d{2,3}(?:\.\d+)?\b', texto_completo)
                if numeros:
                    print(f"    Valores numéricos cercanos: {', '.join(numeros)}")
    
    return info_campo

def main():
    # Ruta al archivo HTML del campo Hierro 3
    archivo_html = "output/paginas_campos/campo_710.html"
    
    # Extraer información
    info_campo = extraer_informacion_campo(archivo_html)
    
    if info_campo:
        print("\nResumen de la información extraída:")
        for clave, valor in info_campo.items():
            print(f"{clave}: {valor}")

if __name__ == "__main__":
    main()
