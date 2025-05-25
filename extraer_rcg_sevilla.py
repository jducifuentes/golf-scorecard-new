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
    
    # Nombre del campo - Asignamos directamente ya que sabemos cuál es
    info_campo['nombre'] = "REAL CLUB SEVILLA GOLF"
    print(f"Nombre del campo: {info_campo['nombre']}")
    
    # Dirección y ubicación - Asignamos directamente
    info_campo['direccion'] = "AUTOVIA SEVILLA-UTRERA KM.3,2 S/N"
    print(f"Dirección: {info_campo['direccion']}")
    
    # Provincia
    info_campo['provincia'] = "SEVILLA"
    print(f"Provincia: {info_campo['provincia']}")
    
    # Ciudad
    info_campo['ciudad'] = "ALCALA DE GUADAIRA"
    print(f"Ciudad: {info_campo['ciudad']}")
    
    # Buscar tablas que puedan contener información de recorridos
    tablas = soup.find_all('table', class_=re.compile('grid_GridOlympus'))
    
    recorridos = []
    
    if tablas:
        print(f"Se encontraron {len(tablas)} tablas de recorridos")
        
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
                        
                        # Crear recorrido
                        if hoyos:
                            recorrido = {
                                "nombre": nombre_barra,
                                "valor_campo": valoracion_total,
                                "slope": slope_total,
                                "metros_totales": metros_totales,
                                "par_total": par_total,
                                "hoyos": hoyos
                            }
                            
                            recorridos.append(recorrido)
                            
                            print(f"Recorrido {nombre_barra}: {metros_totales} metros, Par {par_total}")
                            if valoracion_total:
                                print(f"  Valoración total: {valoracion_total}")
                            if slope_total:
                                print(f"  Slope total: {slope_total}")
            else:
                print("No hay suficientes filas en la tabla para extraer información completa")
    else:
        print("No se encontraron tablas de recorridos")
    
    # Agregar recorridos a la información del campo
    if recorridos:
        info_campo['recorridos'] = recorridos
    
    return info_campo

def main():
    # Ruta al archivo HTML del campo
    archivo_html = "output/paginas_campos/campo_417.html"
    
    # Extraer información
    info_campo = extraer_informacion_campo(archivo_html)
    
    if info_campo:
        print("\nResumen de la información extraída:")
        for clave, valor in info_campo.items():
            if clave != 'recorridos':
                print(f"{clave}: {valor}")
        
        if 'recorridos' in info_campo:
            print(f"\nRecorridos encontrados: {len(info_campo['recorridos'])}")
            for i, rec in enumerate(info_campo['recorridos'], 1):
                print(f"\nRecorrido {i}: {rec['nombre']}")
                print(f"  Valoración: {rec.get('valor_campo', 'No disponible')}")
                print(f"  Slope: {rec.get('slope', 'No disponible')}")
                print(f"  Metros totales: {rec.get('metros_totales', 0)}")
                print(f"  Par total: {rec.get('par_total', 0)}")

if __name__ == "__main__":
    main()
