import sqlite3

def listar_campos():
    """
    Lista todos los campos de golf disponibles en la base de datos.
    """
    # Conectar a la base de datos
    db_path = "db/campos_golf.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener todos los campos
    cursor.execute('''
    SELECT id, nombre, ciudad, provincia, hoyos_totales, par_campo
    FROM campos
    ORDER BY nombre
    ''')
    
    campos = cursor.fetchall()
    
    print(f"Total de campos en la base de datos: {len(campos)}")
    print("=" * 100)
    
    if not campos:
        print("No hay campos en la base de datos.")
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
    
    # Cerrar la conexión
    conn.close()

if __name__ == "__main__":
    listar_campos()
