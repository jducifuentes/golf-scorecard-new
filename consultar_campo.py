import sqlite3
import json
import sys
from tabulate import tabulate

def consultar_campo_por_nombre(nombre_campo):
    """
    Consulta información detallada de un campo de golf por su nombre.
    
    Args:
        nombre_campo (str): Nombre o parte del nombre del campo a buscar.
    """
    # Conectar a la base de datos
    db_path = "db/campos_golf.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Buscar el campo por nombre (usando LIKE para búsqueda parcial)
    cursor.execute('''
    SELECT id, nombre, ciudad, provincia, hoyos_totales, par_campo, id_rfeg, url
    FROM campos
    WHERE nombre LIKE ?
    ''', (f'%{nombre_campo}%',))
    
    campos = cursor.fetchall()
    
    if not campos:
        print(f"No se encontraron campos con el nombre '{nombre_campo}'")
        conn.close()
        return
    
    # Mostrar los campos encontrados
    print(f"Se encontraron {len(campos)} campos con el nombre '{nombre_campo}':")
    print("=" * 80)
    
    for i, campo in enumerate(campos, 1):
        print(f"{i}. ID: {campo['id']} - {campo['nombre']} ({campo['ciudad']}, {campo['provincia']})")
    
    # Si hay más de un campo, pedir al usuario que elija uno
    id_campo = None
    if len(campos) > 1:
        try:
            seleccion = int(input("\nSeleccione el número del campo (1-{}): ".format(len(campos))))
            if 1 <= seleccion <= len(campos):
                id_campo = campos[seleccion - 1]['id']
            else:
                print("Selección inválida.")
                conn.close()
                return
        except ValueError:
            print("Entrada inválida.")
            conn.close()
            return
    else:
        id_campo = campos[0]['id']
    
    # Obtener información detallada del campo seleccionado
    print("\nInformación del campo:")
    print("=" * 80)
    
    campo = None
    for c in campos:
        if c['id'] == id_campo:
            campo = c
            break
    
    print(f"Nombre: {campo['nombre']}")
    print(f"Ciudad: {campo['ciudad']}")
    print(f"Provincia: {campo['provincia']}")
    print(f"Hoyos totales: {campo['hoyos_totales']}")
    print(f"Par del campo: {campo['par_campo']}")
    print(f"ID RFEG: {campo['id_rfeg']}")
    print(f"URL: {campo['url']}")
    
    # Obtener los recorridos del campo
    cursor.execute('''
    SELECT id, nombre, id_recorrido
    FROM recorridos
    WHERE id_campo = ?
    ''', (id_campo,))
    
    recorridos = cursor.fetchall()
    
    print(f"\nRecorridos disponibles ({len(recorridos)}):")
    print("=" * 80)
    
    for i, recorrido in enumerate(recorridos, 1):
        print(f"{i}. {recorrido['nombre']} (ID: {recorrido['id_recorrido']})")
    
    # Si hay más de un recorrido, pedir al usuario que elija uno
    id_recorrido = None
    if len(recorridos) > 1:
        try:
            seleccion = int(input("\nSeleccione el número del recorrido (1-{}): ".format(len(recorridos))))
            if 1 <= seleccion <= len(recorridos):
                id_recorrido = recorridos[seleccion - 1]['id']
            else:
                print("Selección inválida.")
                conn.close()
                return
        except ValueError:
            print("Entrada inválida.")
            conn.close()
            return
    elif len(recorridos) == 1:
        id_recorrido = recorridos[0]['id']
    else:
        print("No hay recorridos disponibles para este campo.")
        conn.close()
        return
    
    # Obtener las barras del recorrido seleccionado
    cursor.execute('''
    SELECT id, nombre, valor_campo, slope
    FROM barras
    WHERE id_recorrido = ?
    ''', (id_recorrido,))
    
    barras = cursor.fetchall()
    
    print(f"\nBarras disponibles ({len(barras)}):")
    print("=" * 80)
    
    for i, barra in enumerate(barras, 1):
        valor_campo = barra['valor_campo'] if barra['valor_campo'] else 'N/A'
        slope = barra['slope'] if barra['slope'] else 'N/A'
        print(f"{i}. {barra['nombre']} (Valoración: {valor_campo}, Slope: {slope})")
    
    # Si hay más de una barra, pedir al usuario que elija una
    id_barra = None
    if len(barras) > 1:
        try:
            seleccion = int(input("\nSeleccione el número de la barra (1-{}): ".format(len(barras))))
            if 1 <= seleccion <= len(barras):
                id_barra = barras[seleccion - 1]['id']
            else:
                print("Selección inválida.")
                conn.close()
                return
        except ValueError:
            print("Entrada inválida.")
            conn.close()
            return
    elif len(barras) == 1:
        id_barra = barras[0]['id']
    else:
        print("No hay barras disponibles para este recorrido.")
        conn.close()
        return
    
    # Obtener los hoyos de la barra seleccionada
    cursor.execute('''
    SELECT numero, metros, par, hcp
    FROM hoyos
    WHERE id_barra = ?
    ORDER BY numero
    ''', (id_barra,))
    
    hoyos = cursor.fetchall()
    
    print(f"\nHoyos del recorrido ({len(hoyos)}):")
    print("=" * 80)
    
    # Preparar los datos para la tabla
    headers = ["Hoyo", "Metros", "Par", "Hcp"]
    tabla = []
    
    total_metros = 0
    total_par = 0
    
    for hoyo in hoyos:
        tabla.append([
            hoyo['numero'],
            hoyo['metros'],
            hoyo['par'],
            hoyo['hcp']
        ])
        total_metros += hoyo['metros']
        total_par += hoyo['par']
    
    # Añadir fila de totales
    tabla.append(["TOTAL", total_metros, total_par, ""])
    
    # Mostrar la tabla
    print(tabulate(tabla, headers=headers, tablefmt="grid"))
    
    # Cerrar la conexión
    conn.close()

def consultar_campo_por_id(id_campo):
    """
    Consulta información detallada de un campo de golf por su ID.
    
    Args:
        id_campo (int): ID del campo a consultar.
    """
    # Conectar a la base de datos
    db_path = "db/campos_golf.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Buscar el campo por ID
    cursor.execute('''
    SELECT id, nombre, ciudad, provincia, hoyos_totales, par_campo, id_rfeg, url
    FROM campos
    WHERE id = ?
    ''', (id_campo,))
    
    campo = cursor.fetchone()
    
    if not campo:
        print(f"No se encontró ningún campo con ID {id_campo}")
        conn.close()
        return
    
    # Mostrar información del campo
    print("\nInformación del campo:")
    print("=" * 80)
    
    print(f"Nombre: {campo['nombre']}")
    print(f"Ciudad: {campo['ciudad']}")
    print(f"Provincia: {campo['provincia']}")
    print(f"Hoyos totales: {campo['hoyos_totales']}")
    print(f"Par del campo: {campo['par_campo']}")
    print(f"ID RFEG: {campo['id_rfeg']}")
    print(f"URL: {campo['url']}")
    
    # Obtener los recorridos del campo
    cursor.execute('''
    SELECT id, nombre, id_recorrido
    FROM recorridos
    WHERE id_campo = ?
    ''', (id_campo,))
    
    recorridos = cursor.fetchall()
    
    print(f"\nRecorridos disponibles ({len(recorridos)}):")
    print("=" * 80)
    
    for i, recorrido in enumerate(recorridos, 1):
        print(f"{i}. {recorrido['nombre']} (ID: {recorrido['id_recorrido']})")
        
        # Obtener las barras del recorrido
        cursor.execute('''
        SELECT id, nombre, valor_campo, slope
        FROM barras
        WHERE id_recorrido = ?
        ''', (recorrido['id'],))
        
        barras = cursor.fetchall()
        
        print(f"   Barras disponibles ({len(barras)}):")
        
        for j, barra in enumerate(barras, 1):
            valor_campo = barra['valor_campo'] if barra['valor_campo'] else 'N/A'
            slope = barra['slope'] if barra['slope'] else 'N/A'
            print(f"   {j}. {barra['nombre']} (Valoración: {valor_campo}, Slope: {slope})")
            
            # Obtener los hoyos de la barra
            cursor.execute('''
            SELECT COUNT(*) as total_hoyos, SUM(metros) as total_metros, SUM(par) as total_par
            FROM hoyos
            WHERE id_barra = ?
            ''', (barra['id'],))
            
            resumen = cursor.fetchone()
            
            if resumen and resumen['total_hoyos'] > 0:
                print(f"      Hoyos: {resumen['total_hoyos']}, Metros totales: {resumen['total_metros']}, Par total: {resumen['total_par']}")
            else:
                print("      No hay información de hoyos para esta barra")
    
    # Cerrar la conexión
    conn.close()

def consultar_campo_por_id_detallado(id_campo):
    """
    Consulta información detallada de un campo de golf por su ID, incluyendo todos los hoyos.
    
    Args:
        id_campo (int): ID del campo a consultar.
    """
    # Conectar a la base de datos
    db_path = "db/campos_golf.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Buscar el campo por ID
    cursor.execute('''
    SELECT id, nombre, ciudad, provincia, hoyos_totales, par_campo, id_rfeg, url
    FROM campos
    WHERE id = ?
    ''', (id_campo,))
    
    campo = cursor.fetchone()
    
    if not campo:
        print(f"No se encontró ningún campo con ID {id_campo}")
        conn.close()
        return
    
    # Mostrar información del campo
    print("\nInformación del campo:")
    print("=" * 80)
    
    print(f"Nombre: {campo['nombre']}")
    print(f"Ciudad: {campo['ciudad']}")
    print(f"Provincia: {campo['provincia']}")
    print(f"Hoyos totales: {campo['hoyos_totales']}")
    print(f"Par del campo: {campo['par_campo']}")
    print(f"ID RFEG: {campo['id_rfeg']}")
    print(f"URL: {campo['url']}")
    
    # Obtener los recorridos del campo
    cursor.execute('''
    SELECT id, nombre, id_recorrido
    FROM recorridos
    WHERE id_campo = ?
    ''', (id_campo,))
    
    recorridos = cursor.fetchall()
    
    print(f"\nRecorridos disponibles ({len(recorridos)}):")
    print("=" * 80)
    
    for i, recorrido in enumerate(recorridos, 1):
        print(f"\nRecorrido {i}: {recorrido['nombre']} (ID: {recorrido['id_recorrido']})")
        
        # Obtener las barras del recorrido
        cursor.execute('''
        SELECT id, nombre, valor_campo, slope
        FROM barras
        WHERE id_recorrido = ?
        ''', (recorrido['id'],))
        
        barras = cursor.fetchall()
        
        print(f"Barras disponibles ({len(barras)}):")
        
        for j, barra in enumerate(barras, 1):
            valor_campo = barra['valor_campo'] if barra['valor_campo'] else 'N/A'
            slope = barra['slope'] if barra['slope'] else 'N/A'
            print(f"\n  Barra {j}: {barra['nombre']} (Valoración: {valor_campo}, Slope: {slope})")
            
            # Obtener los hoyos de la barra
            cursor.execute('''
            SELECT numero, metros, par, hcp
            FROM hoyos
            WHERE id_barra = ?
            ORDER BY numero
            ''', (barra['id'],))
            
            hoyos = cursor.fetchall()
            
            if hoyos:
                # Preparar los datos para la tabla
                headers = ["Hoyo", "Metros", "Par", "Hcp"]
                tabla = []
                
                total_metros = 0
                total_par = 0
                
                for hoyo in hoyos:
                    tabla.append([
                        hoyo['numero'],
                        hoyo['metros'],
                        hoyo['par'],
                        hoyo['hcp']
                    ])
                    if hoyo['metros']:
                        total_metros += hoyo['metros']
                    if hoyo['par']:
                        total_par += hoyo['par']
                
                # Añadir fila de totales
                tabla.append(["TOTAL", total_metros, total_par, ""])
                
                # Mostrar la tabla
                print(tabulate(tabla, headers=headers, tablefmt="grid"))
            else:
                print("  No hay información de hoyos para esta barra")
    
    # Cerrar la conexión
    conn.close()

def buscar_olimpico_leon():
    """
    Busca específicamente el campo Olímpico de León y muestra sus recorridos y hoyos.
    """
    # Conectar a la base de datos
    db_path = "db/campos_golf.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Buscar el campo Olímpico de León
    cursor.execute('''
    SELECT id, nombre, ciudad, provincia, hoyos_totales, par_campo, id_rfeg, url
    FROM campos
    WHERE nombre LIKE ?
    ''', ('%León%',))
    
    campos = cursor.fetchall()
    
    if not campos:
        print("No se encontró el campo Olímpico de León")
        conn.close()
        return
    
    # Mostrar los campos encontrados
    print(f"Se encontraron {len(campos)} campos relacionados con León:")
    print("=" * 80)
    
    campo_olimpico = None
    for campo in campos:
        print(f"ID: {campo['id']} - {campo['nombre']} ({campo['ciudad']}, {campo['provincia']})")
        if "Olímpico" in campo['nombre'] or "LEÓN" in campo['nombre'].upper():
            campo_olimpico = campo
    
    if not campo_olimpico:
        if len(campos) > 0:
            campo_olimpico = campos[0]
        else:
            print("No se pudo identificar el campo Olímpico de León")
            conn.close()
            return
    
    print("\nInformación del campo seleccionado:")
    print("=" * 80)
    
    print(f"Nombre: {campo_olimpico['nombre']}")
    print(f"Ciudad: {campo_olimpico['ciudad']}")
    print(f"Provincia: {campo_olimpico['provincia']}")
    print(f"Hoyos totales: {campo_olimpico['hoyos_totales']}")
    print(f"Par del campo: {campo_olimpico['par_campo']}")
    
    # Obtener los recorridos del campo
    cursor.execute('''
    SELECT id, nombre, id_recorrido
    FROM recorridos
    WHERE id_campo = ?
    ''', (campo_olimpico['id'],))
    
    recorridos = cursor.fetchall()
    
    print(f"\nRecorridos disponibles ({len(recorridos)}):")
    print("=" * 80)
    
    for recorrido in recorridos:
        print(f"Recorrido: {recorrido['nombre']} (ID: {recorrido['id_recorrido']})")
        
        # Obtener las barras del recorrido
        cursor.execute('''
        SELECT id, nombre, valor_campo, slope
        FROM barras
        WHERE id_recorrido = ?
        ''', (recorrido['id'],))
        
        barras = cursor.fetchall()
        
        for barra in barras:
            valor_campo = barra['valor_campo'] if barra['valor_campo'] else 'N/A'
            slope = barra['slope'] if barra['slope'] else 'N/A'
            print(f"\n  Barra: {barra['nombre']} (Valoración: {valor_campo}, Slope: {slope})")
            
            # Obtener los hoyos de la barra
            cursor.execute('''
            SELECT numero, metros, par, hcp
            FROM hoyos
            WHERE id_barra = ?
            ORDER BY numero
            ''', (barra['id'],))
            
            hoyos = cursor.fetchall()
            
            if hoyos:
                # Preparar los datos para la tabla
                headers = ["Hoyo", "Metros", "Par", "Hcp"]
                tabla = []
                
                total_metros = 0
                total_par = 0
                
                for hoyo in hoyos:
                    tabla.append([
                        hoyo['numero'],
                        hoyo['metros'],
                        hoyo['par'],
                        hoyo['hcp']
                    ])
                    total_metros += hoyo['metros']
                    total_par += hoyo['par']
                
                # Añadir fila de totales
                tabla.append(["TOTAL", total_metros, total_par, ""])
                
                # Mostrar la tabla
                print(tabulate(tabla, headers=headers, tablefmt="grid"))
            else:
                print("  No hay información de hoyos para esta barra")
    
    # Cerrar la conexión
    conn.close()

def consultar_campo_por_nombre_no_interactivo(nombre_campo):
    """
    Consulta información detallada de un campo de golf por su nombre sin interacción del usuario.
    
    Args:
        nombre_campo (str): Nombre o parte del nombre del campo a buscar.
    """
    # Conectar a la base de datos
    db_path = "db/campos_golf.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Buscar el campo por nombre (usando LIKE para búsqueda parcial)
    cursor.execute('''
    SELECT id, nombre, ciudad, provincia, hoyos_totales, par_campo, id_rfeg, url
    FROM campos
    WHERE nombre LIKE ?
    ''', (f'%{nombre_campo}%',))
    
    campos = cursor.fetchall()
    
    if not campos:
        print(f"No se encontraron campos con el nombre '{nombre_campo}'")
        conn.close()
        return
    
    # Mostrar los campos encontrados
    print(f"Se encontraron {len(campos)} campos con el nombre '{nombre_campo}':")
    print("=" * 80)
    
    for i, campo in enumerate(campos, 1):
        print(f"{i}. ID: {campo['id']} - {campo['nombre']} ({campo['ciudad']}, {campo['provincia']})")
    
    # Usar el primer campo encontrado
    id_campo = campos[0]['id']
    
    # Obtener información detallada del campo seleccionado
    print("\nInformación del campo:")
    print("=" * 80)
    
    campo = campos[0]
    
    print(f"Nombre: {campo['nombre']}")
    print(f"Ciudad: {campo['ciudad']}")
    print(f"Provincia: {campo['provincia']}")
    print(f"Hoyos totales: {campo['hoyos_totales']}")
    print(f"Par del campo: {campo['par_campo']}")
    print(f"ID RFEG: {campo['id_rfeg']}")
    print(f"URL: {campo['url']}")
    
    # Obtener los recorridos del campo
    cursor.execute('''
    SELECT id, nombre, id_recorrido
    FROM recorridos
    WHERE id_campo = ?
    ''', (id_campo,))
    
    recorridos = cursor.fetchall()
    
    print(f"\nRecorridos disponibles ({len(recorridos)}):")
    print("=" * 80)
    
    for i, recorrido in enumerate(recorridos, 1):
        print(f"{i}. {recorrido['nombre']} (ID: {recorrido['id_recorrido']})")
        
        # Obtener las barras del recorrido
        cursor.execute('''
        SELECT id, nombre, valor_campo, slope
        FROM barras
        WHERE id_recorrido = ?
        ''', (recorrido['id'],))
        
        barras = cursor.fetchall()
        
        print(f"\n   Barras disponibles ({len(barras)}):")
        
        for j, barra in enumerate(barras, 1):
            valor_campo = barra['valor_campo'] if barra['valor_campo'] else 'N/A'
            slope = barra['slope'] if barra['slope'] else 'N/A'
            print(f"   {j}. {barra['nombre']} (Valoración: {valor_campo}, Slope: {slope})")
            
            # Obtener los hoyos de la barra
            cursor.execute('''
            SELECT numero, metros, par, hcp
            FROM hoyos
            WHERE id_barra = ?
            ORDER BY numero
            ''', (barra['id'],))
            
            hoyos = cursor.fetchall()
            
            if hoyos:
                # Preparar los datos para la tabla
                headers = ["Hoyo", "Metros", "Par", "Hcp"]
                tabla = []
                
                total_metros = 0
                total_par = 0
                
                for hoyo in hoyos:
                    tabla.append([
                        hoyo['numero'],
                        hoyo['metros'],
                        hoyo['par'],
                        hoyo['hcp']
                    ])
                    if hoyo['metros']:
                        total_metros += hoyo['metros']
                    if hoyo['par']:
                        total_par += hoyo['par']
                
                # Añadir fila de totales
                tabla.append(["TOTAL", total_metros, total_par, ""])
                
                # Mostrar la tabla
                print(tabulate(tabla, headers=headers, tablefmt="grid"))
            else:
                print("      No hay información de hoyos para esta barra")
    
    # Cerrar la conexión
    conn.close()

if __name__ == "__main__":
    # Verificar si se pasó un argumento
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            # Si el argumento es un número, buscar por ID
            if len(sys.argv) > 2 and sys.argv[2].lower() == "detallado":
                consultar_campo_por_id_detallado(int(sys.argv[1]))
            else:
                consultar_campo_por_id(int(sys.argv[1]))
        else:
            # Si el argumento es texto, buscar por nombre (modo no interactivo)
            consultar_campo_por_nombre_no_interactivo(sys.argv[1])
    else:
        # Si no se pasaron argumentos, buscar específicamente el Olímpico de León
        buscar_olimpico_leon()
