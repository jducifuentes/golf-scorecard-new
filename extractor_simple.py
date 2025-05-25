import requests
from bs4 import BeautifulSoup
import json
import os
import time

def obtener_campos_golf():
    """
    Extrae todos los campos de golf de España con hoyos > 0
    """
    # URL de búsqueda
    url = "https://rfegolf.es/ClubPaginas/ClubSearchResult.aspx"
    
    # Headers para simular un navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    }
    
    # Crear sesión
    session = requests.Session()
    
    # Crear directorio de salida si no existe
    os.makedirs("output", exist_ok=True)
    
    # Paso 1: Obtener la página inicial
    print("Obteniendo página inicial...")
    response = session.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extraer datos del formulario
    form_data = {}
    
    # Extraer campos ocultos
    hidden_inputs = soup.find_all("input", {"type": "hidden"})
    for hidden_input in hidden_inputs:
        name = hidden_input.get("name")
        value = hidden_input.get("value", "")
        if name:
            form_data[name] = value
    
    # Buscar checkboxes de hoyos
    checkbox_9 = soup.find("input", {"id": lambda x: x and "chk9" in x.lower()})
    checkbox_18 = soup.find("input", {"id": lambda x: x and "chk18" in x.lower()})
    checkbox_27 = soup.find("input", {"id": lambda x: x and "chk27" in x.lower()})
    checkbox_36 = soup.find("input", {"id": lambda x: x and "chk36" in x.lower()})
    
    # Añadir checkboxes al formulario
    if checkbox_9:
        form_data[checkbox_9.get("name")] = "on"
        print("Seleccionando campos con 9 hoyos")
    
    if checkbox_18:
        form_data[checkbox_18.get("name")] = "on"
        print("Seleccionando campos con 18 hoyos")
    
    if checkbox_27:
        form_data[checkbox_27.get("name")] = "on"
        print("Seleccionando campos con 27 hoyos")
    
    if checkbox_36:
        form_data[checkbox_36.get("name")] = "on"
        print("Seleccionando campos con 36 o más hoyos")
    
    # Buscar botón de búsqueda
    btn_search = soup.find("input", {"id": lambda x: x and "btnSearch" in x})
    if btn_search:
        form_data[btn_search.get("name")] = "Buscar"
    
    # Guardar datos del formulario para depuración
    with open("output/form_data.json", "w", encoding="utf-8") as f:
        json.dump(form_data, f, indent=2, ensure_ascii=False)
    
    # Paso 2: Enviar formulario para buscar
    print("Realizando búsqueda...")
    response = session.post(url, data=form_data, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Guardar página de resultados para depuración
    with open("output/search_results.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    
    # Extraer resultados
    campos = []
    pagina = 1
    
    while True:
        print(f"Procesando página {pagina}...")
        
        # Buscar tabla de resultados
        tabla = soup.find("table", {"id": lambda x: x and "gvSearchResult" in x})
        
        if not tabla:
            print("No se encontró la tabla de resultados.")
            break
        
        # Buscar filas de la tabla
        filas = tabla.find_all("tr")
        
        if len(filas) <= 1:
            print("No se encontraron resultados en la tabla.")
            break
        
        print(f"Encontradas {len(filas)-1} filas en la página {pagina}")
        
        # Procesar cada fila (excepto la primera que es el encabezado)
        for fila in filas[1:]:
            # Buscar celdas de la fila
            celdas = fila.find_all("td")
            
            if len(celdas) >= 6:
                # Extraer datos del club
                enlace = celdas[1].find("a")
                
                if enlace:
                    url_club = enlace.get("href")
                    id_club = url_club.split("ClubId=")[1].split("&")[0] if "ClubId=" in url_club else None
                    nombre = enlace.text.strip()
                    
                    # Extraer otros datos
                    ciudad = celdas[2].text.strip()
                    provincia = celdas[3].text.strip()
                    hoyos = celdas[4].text.strip()
                    hoyos_cortos = celdas[5].text.strip()
                    
                    # Convertir hoyos a entero
                    try:
                        num_hoyos = int(hoyos)
                    except ValueError:
                        num_hoyos = 0
                    
                    # Solo incluir campos con hoyos > 0
                    if num_hoyos > 0:
                        datos_campo = {
                            "id": id_club,
                            "nombre": nombre,
                            "url": "https://rfegolf.es" + url_club.lstrip("/"),
                            "ciudad": ciudad,
                            "provincia": provincia,
                            "hoyos": num_hoyos,
                            "hoyos_cortos": hoyos_cortos
                        }
                        campos.append(datos_campo)
                        print(f"Campo encontrado: {nombre} - {ciudad}, {provincia} - Hoyos: {hoyos}")
        
        # Verificar si hay más páginas
        boton_siguiente = soup.find("input", {"class": "pagnext"})
        
        if boton_siguiente and "disabled" not in boton_siguiente.get("disabled", []):
            # Extraer datos del formulario para la paginación
            form_data = {}
            
            # Extraer campos ocultos
            hidden_inputs = soup.find_all("input", {"type": "hidden"})
            for hidden_input in hidden_inputs:
                name = hidden_input.get("name")
                value = hidden_input.get("value", "")
                if name:
                    form_data[name] = value
            
            # Establecer el evento para ir a la página siguiente
            form_data["__EVENTTARGET"] = boton_siguiente.get("name", "")
            form_data["__EVENTARGUMENT"] = ""
            
            # Esperar un poco para no sobrecargar el servidor
            time.sleep(2)
            
            # Enviar formulario para ir a la página siguiente
            response = session.post(url, data=form_data, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Guardar página de resultados para depuración
            with open(f"output/search_results_page{pagina+1}.html", "w", encoding="utf-8") as f:
                f.write(str(soup))
            
            pagina += 1
        else:
            break
    
    print(f"Se encontraron {len(campos)} campos de golf con hoyos > 0 en España.")
    return campos

# Ejecutar el script
if __name__ == "__main__":
    print("Extrayendo campos de golf de España...")
    campos = obtener_campos_golf()
    
    # Guardar resultados en un archivo JSON
    with open("output/campos_golf.json", "w", encoding="utf-8") as f:
        json.dump(campos, f, indent=2, ensure_ascii=False)
    
    print("Proceso completado. Resultados guardados en output/campos_golf.json")
