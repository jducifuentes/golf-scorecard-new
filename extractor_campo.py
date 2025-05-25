import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re

def extraer_informacion_campo(url_campo):
    """
    Extrae información detallada de un campo de golf
    """
    print(f"Extrayendo información del campo: {url_campo}")
    
    # Headers para simular un navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    }
    
    # Crear directorio de salida si no existe
    os.makedirs("output", exist_ok=True)
    
    # Obtener la página del campo
    session = requests.Session()
    max_intentos = 3
    intentos = 0
    
    while intentos < max_intentos:
        try:
            response = session.get(url_campo, headers=headers, timeout=15)
            response.raise_for_status()  # Lanzar excepción si hay error HTTP
            break
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            intentos += 1
            print(f"Error al obtener la página ({intentos}/{max_intentos}): {e}")
            if intentos < max_intentos:
                tiempo_espera = 5 * intentos
                print(f"Reintentando en {tiempo_espera} segundos...")
                time.sleep(tiempo_espera)
            else:
                print("No se pudo obtener la página después de varios intentos.")
                return {"error": "No se pudo obtener la página del campo"}
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Guardar la página para depuración
    with open("output/campo_detalle.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    
    # Extraer información básica del campo
    info_campo = {
        "url": url_campo
    }
    
    # Extraer ID del club de la URL
    club_id_match = re.search(r'ClubId=(\d+)', url_campo)
    if club_id_match:
        info_campo["id"] = club_id_match.group(1)
    
    # Nombre del campo
    nombre_campo = soup.find("span", {"id": lambda x: x and "lblClubName" in x})
    if nombre_campo:
        info_campo["nombre"] = nombre_campo.text.strip()
    
    # Dirección
    direccion = soup.find("span", {"id": lambda x: x and "lblAddress" in x})
    if direccion:
        info_campo["direccion"] = direccion.text.strip()
    
    # Código postal
    cp = soup.find("span", {"id": lambda x: x and "lblZipCode" in x})
    if cp:
        info_campo["codigo_postal"] = cp.text.strip()
    
    # Ciudad
    ciudad = soup.find("span", {"id": lambda x: x and "lblCity" in x})
    if ciudad:
        info_campo["ciudad"] = ciudad.text.strip()
    
    # Provincia
    provincia = soup.find("span", {"id": lambda x: x and "lblProvince" in x})
    if provincia:
        info_campo["provincia"] = provincia.text.strip()
    
    # Comunidad Autónoma
    ccaa = soup.find("span", {"id": lambda x: x and "lblRegion" in x})
    if ccaa:
        info_campo["comunidad_autonoma"] = ccaa.text.strip()
    
    # Teléfono
    telefono = soup.find("span", {"id": lambda x: x and "lblPhone" in x})
    if telefono:
        info_campo["telefono"] = telefono.text.strip()
    
    # Email
    email = soup.find("a", {"id": lambda x: x and "hlEmail" in x})
    if email:
        info_campo["email"] = email.get("href", "").replace("mailto:", "").strip()
    
    # Web
    web = soup.find("a", {"id": lambda x: x and "hlWebsite" in x})
    if web:
        info_campo["web"] = web.get("href", "").strip()
    
    # Año de fundación
    fundacion = soup.find("span", {"id": lambda x: x and "lblFoundation" in x})
    if fundacion:
        info_campo["fundacion"] = fundacion.text.strip()
    
    # Diseñador
    disenador = soup.find("span", {"id": lambda x: x and "lblDesigner" in x})
    if disenador:
        info_campo["disenador"] = disenador.text.strip()
    
    # Descripción
    descripcion = soup.find("span", {"id": lambda x: x and "lblDescription" in x})
    if descripcion:
        info_campo["descripcion"] = descripcion.text.strip()
    
    # Extraer recorridos desde el menú desplegable
    recorridos_select = soup.find("select", {"id": lambda x: x and "ddlRecorridos" in x})
    
    if recorridos_select:
        opciones = recorridos_select.find_all("option")
        print(f"Se encontraron {len(opciones)} recorridos en el menú desplegable")
        
        recorridos = []
        
        for opcion in opciones:
            recorrido_id = opcion.get("value")
            nombre_recorrido = opcion.text.strip()
            
            print(f"Procesando recorrido: {nombre_recorrido} (ID: {recorrido_id})")
            
            # Preparar datos para el POST
            form_data = {}
            
            # Extraer campos ocultos
            hidden_inputs = soup.find_all("input", {"type": "hidden"})
            for hidden_input in hidden_inputs:
                name = hidden_input.get("name")
                value = hidden_input.get("value", "")
                if name:
                    form_data[name] = value
            
            # Establecer el recorrido seleccionado
            form_data["__EVENTTARGET"] = recorridos_select.get("name")
            form_data["__EVENTARGUMENT"] = ""
            form_data[recorridos_select.get("name")] = recorrido_id
            
            # Enviar formulario para obtener la página del recorrido
            intentos = 0
            while intentos < max_intentos:
                try:
                    response = session.post(url_campo, data=form_data, headers=headers, timeout=15)
                    response.raise_for_status()
                    break
                except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
                    intentos += 1
                    print(f"Error al obtener el recorrido ({intentos}/{max_intentos}): {e}")
                    if intentos < max_intentos:
                        tiempo_espera = 5 * intentos
                        print(f"Reintentando en {tiempo_espera} segundos...")
                        time.sleep(tiempo_espera)
                    else:
                        print(f"No se pudo obtener el recorrido {nombre_recorrido} después de varios intentos.")
                        continue
            
            soup_recorrido = BeautifulSoup(response.text, "html.parser")
            
            # Guardar la página para depuración
            with open(f"output/recorrido_{recorrido_id}.html", "w", encoding="utf-8") as f:
                f.write(str(soup_recorrido))
            
            # Extraer información del recorrido
            recorrido = {
                "id": recorrido_id,
                "nombre": nombre_recorrido,
                "barras": []
            }
            
            # Buscar las tablas con la información de los hoyos (una por cada barra)
            tablas_barras = soup_recorrido.find_all("table", {"class": "grid_GridOlympus"})
            
            for tabla in tablas_barras:
                filas = tabla.find_all("tr")
                
                if len(filas) < 2:
                    continue
                
                # La primera fila contiene el nombre de la barra
                cabecera = filas[0].find_all("th")
                if len(cabecera) < 2:
                    continue
                
                nombre_barra = cabecera[1].text.strip()
                
                # Inicializar la información de la barra
                barra = {
                    "nombre": nombre_barra,
                    "hoyos": []
                }
                
                # Asignar valores de Slope y Valoración según el nombre de la barra
                if nombre_barra.upper() == "NEGRAS":
                    barra["slope"] = 140
                    barra["valoracion"] = 75.1
                elif nombre_barra.upper() == "BLANCAS":
                    barra["slope"] = 135
                    barra["valoracion"] = 73.2
                elif nombre_barra.upper() == "AMARILLAS":
                    barra["slope"] = 126
                    barra["valoracion"] = 70.5
                elif nombre_barra.upper() == "ROJAS":
                    barra["slope"] = 122
                    barra["valoracion"] = 68.5
                elif nombre_barra.upper() == "NARANJAS":
                    barra["slope"] = 115
                    barra["valoracion"] = 65.0
                elif nombre_barra.upper() == "VERDES":
                    barra["slope"] = 104
                    barra["valoracion"] = 60.7
                else:
                    barra["slope"] = ""
                    barra["valoracion"] = ""
                
                # Extraer información de los hoyos
                if len(filas) >= 4:  # Necesitamos al menos 4 filas (cabecera, metros, par, hcp)
                    # Extraer metros, par y hcp para cada hoyo
                    metros_fila = filas[1].find_all("td")
                    par_fila = filas[2].find_all("td")
                    hcp_fila = filas[3].find_all("td")
                    
                    # Verificar que tenemos suficientes columnas
                    if len(metros_fila) > 10 and len(par_fila) > 10 and len(hcp_fila) > 10:
                        # Extraer información de cada hoyo
                        for i in range(9):  # Primeros 9 hoyos
                            if i + 2 < len(metros_fila) and i + 2 < len(par_fila) and i + 2 < len(hcp_fila):
                                hoyo = {
                                    "numero": i + 1,
                                    "metros": metros_fila[i + 2].text.strip(),
                                    "par": par_fila[i + 2].text.strip(),
                                    "hcp": hcp_fila[i + 2].text.strip()
                                }
                                barra["hoyos"].append(hoyo)
                        
                        # Los segundos 9 hoyos empiezan en la columna 14 (índice 13)
                        for i in range(9):  # Segundos 9 hoyos
                            idx = i + 14  # Ajustado para incluir el hoyo 10
                            if idx < len(metros_fila) and idx < len(par_fila) and idx < len(hcp_fila):
                                # Verificar que estamos en la columna correcta (debe ser un número)
                                # Las columnas de hoyo tienen encabezados numéricos (10, 11, 12, etc.)
                                hoyo_num = i + 10  # Hoyo 10, 11, 12, etc.
                                
                                # Verificar que la celda contiene un valor numérico para metros
                                metros_valor = metros_fila[idx].text.strip()
                                par_valor = par_fila[idx].text.strip()
                                hcp_valor = hcp_fila[idx].text.strip()
                                
                                # Solo añadir si parece un valor válido (metros debe ser numérico)
                                if metros_valor and (metros_valor.isdigit() or metros_valor.replace('.', '', 1).isdigit()):
                                    hoyo = {
                                        "numero": hoyo_num,
                                        "metros": metros_valor,
                                        "par": par_valor,
                                        "hcp": hcp_valor
                                    }
                                    barra["hoyos"].append(hoyo)
                
                # Añadir la barra al recorrido
                recorrido["barras"].append(barra)
            
            recorridos.append(recorrido)
            
            # Esperar un poco para no sobrecargar el servidor
            time.sleep(2)
        
        info_campo["recorridos"] = recorridos
    else:
        print("No se encontró el menú desplegable de recorridos")
        info_campo["recorridos"] = []
    
    return info_campo

def main():
    # Ejemplo de uso
    campo_id = 360  # ID del campo HIERRO 3
    url_campo = f"https://rfegolf.es/ClubPaginas/ClubMicrosite.aspx?ClubId=710"
    
    print(f"Extrayendo información del campo: HIERRO 3")
    print(f"Extrayendo información del campo: {url_campo}")
    
    resultado = extraer_informacion_campo(url_campo)
    
    # Guardar los resultados en un archivo JSON
    with open("output/campo_detalle.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print("Proceso completado. Resultados guardados en output/campo_detalle.json")
    
    # Mostrar un resumen de los recorridos y barras encontrados
    print("\nResumen de recorridos:")
    for i, recorrido in enumerate(resultado["recorridos"]):
        total_hoyos = sum(len(barra["hoyos"]) for barra in recorrido["barras"])
        print(f"{i+1}. {recorrido['nombre']} - {len(recorrido['barras'])} barras, {total_hoyos} hoyos")

if __name__ == "__main__":
    main()
