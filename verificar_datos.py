import sqlite3

def verificar_datos():
    # Conectar a la base de datos
    conn = sqlite3.connect('golf_scorecard.db')
    cursor = conn.cursor()
    
    # Consultar campos
    print("CAMPOS:")
    cursor.execute("SELECT id, nombre, ciudad, provincia FROM campos")
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Nombre: {row[1]}, Ciudad: {row[2]}, Provincia: {row[3]}")
    
    print("\nRECORRIDOS:")
    cursor.execute("""
    SELECT r.id, c.nombre, r.nombre 
    FROM recorridos r 
    JOIN campos c ON r.id_campo = c.id
    """)
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Campo: {row[1]}, Recorrido: {row[2]}")
    
    print("\nBARRAS:")
    cursor.execute("""
    SELECT b.id, r.nombre, b.nombre, b.valor_campo, b.slope 
    FROM barras b 
    JOIN recorridos r ON b.id_recorrido = r.id
    """)
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Recorrido: {row[1]}, Barra: {row[2]}, Valor Campo: {row[3]}, Slope: {row[4]}")
    
    print("\nHOYOS (muestra de 5 primeros):")
    cursor.execute("""
    SELECT h.id, b.nombre, h.numero, h.par, h.metros, h.hcp 
    FROM hoyos h 
    JOIN barras b ON h.id_barra = b.id
    LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Barra: {row[1]}, Hoyo: {row[2]}, Par: {row[3]}, Metros: {row[4]}, HCP: {row[5]}")
    
    # Cerrar la conexión
    conn.close()

if __name__ == "__main__":
    verificar_datos()
