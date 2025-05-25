import sqlite3
import sys

def listar_campos_por_provincia(provincia):
    """
    Lista todos los campos de golf de una provincia específica.
    
    Args:
        provincia (str): Nombre de la provincia a buscar.
    """
    # Conectar a la base de datos
    db_path = "db/campos_golf.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Buscar campos por provincia (usando LIKE para búsqueda parcial)
    cursor.execute('''
    SELECT id, nombre, ciudad, provincia, hoyos_totales, par_campo, id_rfeg, url
    FROM campos
    WHERE provincia LIKE ?
    ORDER BY nombre
    ''', (f'%{provincia}%',))
    
    campos = cursor.fetchall()
    
    print(f"Campos de golf en la provincia de {provincia}: {len(campos)}")
    print("=" * 100)
    
    if not campos:
        print(f"No se encontraron campos en la provincia de {provincia}")
    else:
        print(f"{'ID':<4} {'Nombre':<40} {'Ciudad':<20} {'Provincia':<15} {'Hoyos':<6} {'Par':<4}")
        print("-" * 100)
        
        for campo in campos:
            nombre = campo['nombre'] if campo['nombre'] else 'N/A'
            ciudad = campo['ciudad'] if campo['ciudad'] else 'N/A'
            provincia = campo['provincia'] if campo['provincia'] else 'N/A'
            hoyos = campo['hoyos_totales'] if campo['hoyos_totales'] else 'N/A'
            par = campo['par_campo'] if campo['par_campo'] else 'N/A'
            
            print(f"{campo['id']:<4} {nombre[:40]:<40} {ciudad[:20]:<20} {provincia[:15]:<15} {hoyos:<6} {par:<4}")
            
            # Obtener los recorridos del campo
            cursor.execute('''
            SELECT nombre, id_recorrido
            FROM recorridos
            WHERE id_campo = ?
            ''', (campo['id'],))
            
            recorridos = cursor.fetchall()
            
            for recorrido in recorridos:
                print(f"    - Recorrido: {recorrido['nombre']} (ID: {recorrido['id_recorrido']})")
    
    # Cerrar la conexión
    conn.close()

if __name__ == "__main__":
    # Verificar si se pasó un argumento
    if len(sys.argv) > 1:
        provincia = sys.argv[1]
    else:
        provincia = input("Introduce el nombre de la provincia: ")
    
    listar_campos_por_provincia(provincia)
