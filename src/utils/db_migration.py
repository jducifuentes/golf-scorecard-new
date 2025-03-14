"""
Utilidades para migrar la base de datos a nuevas versiones.
"""
import json
import sqlite3
from colorama import Fore, Style


def migrate_scorecards_add_handicap_strokes(db_path):
    """
    Migra la tabla de tarjetas para añadir el campo handicap_strokes.
    
    Args:
        db_path (str): Ruta al archivo de base de datos
        
    Returns:
        tuple: (éxito, mensaje)
    """
    try:
        print(f"{Fore.YELLOW}Iniciando migración de la base de datos...{Style.RESET_ALL}")
        
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(scorecards)")
        columns = cursor.fetchall()
        column_names = [column['name'] for column in columns]
        
        if 'handicap_strokes' in column_names:
            print(f"{Fore.GREEN}La columna 'handicap_strokes' ya existe. No es necesaria la migración.{Style.RESET_ALL}")
            conn.close()
            return True, "La columna ya existe"
        
        # Crear tabla temporal con la nueva estructura
        print(f"{Fore.YELLOW}Creando tabla temporal con la nueva estructura...{Style.RESET_ALL}")
        cursor.execute('''
            CREATE TABLE scorecards_temp (
                id INTEGER PRIMARY KEY,
                player_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                strokes TEXT NOT NULL,
                handicap_strokes TEXT NOT NULL,
                points TEXT NOT NULL,
                handicap_coefficient INTEGER NOT NULL,
                playing_handicap REAL,
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        ''')
        
        # Obtener todas las tarjetas existentes
        print(f"{Fore.YELLOW}Migrando datos existentes...{Style.RESET_ALL}")
        cursor.execute("SELECT * FROM scorecards")
        scorecards = cursor.fetchall()
        
        # Migrar datos a la nueva tabla
        for scorecard in scorecards:
            # Convertir strokes a lista
            strokes_json = scorecard['strokes']
            strokes = json.loads(strokes_json)
            
            # Calcular handicap_strokes basado en strokes y playing_handicap
            handicap_strokes = []
            
            # Si hay un hándicap de juego, calcular los golpes netos
            if scorecard['playing_handicap'] is not None:
                # Obtener información del campo
                cursor.execute("SELECT * FROM courses WHERE id = ?", (scorecard['course_id'],))
                course = cursor.fetchone()
                
                if course:
                    # Obtener hándicaps de hoyo
                    hole_handicaps = json.loads(course['hole_handicaps'])
                    
                    # Calcular golpes de hándicap por hoyo
                    playing_handicap = int(round(scorecard['playing_handicap']))
                    
                    for i, stroke in enumerate(strokes):
                        if i < len(hole_handicaps):
                            hole_handicap = hole_handicaps[i]
                            
                            # Asignar golpes de hándicap según el sistema estándar
                            handicap_stroke = stroke
                            
                            if hole_handicap <= playing_handicap:
                                # Restar un golpe
                                handicap_stroke = max(0, stroke - 1)
                                
                                # Si el hándicap es mayor que 18, puede recibir golpes adicionales
                                if playing_handicap > 18 and hole_handicap <= (playing_handicap - 18):
                                    handicap_stroke = max(0, handicap_stroke - 1)
                            
                            handicap_strokes.append(handicap_stroke)
                        else:
                            # Si no hay información de hándicap para este hoyo, usar el mismo valor
                            handicap_strokes.append(stroke)
                else:
                    # Si no hay información del campo, usar los mismos valores
                    handicap_strokes = strokes.copy()
            else:
                # Si no hay hándicap de juego, los golpes netos son iguales a los brutos
                handicap_strokes = strokes.copy()
            
            # Convertir a JSON
            handicap_strokes_json = json.dumps(handicap_strokes)
            
            # Insertar en la tabla temporal
            cursor.execute('''
                INSERT INTO scorecards_temp (
                    id, player_id, course_id, date, strokes, handicap_strokes, points, 
                    handicap_coefficient, playing_handicap
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scorecard['id'], scorecard['player_id'], scorecard['course_id'],
                scorecard['date'], scorecard['strokes'], handicap_strokes_json,
                scorecard['points'], scorecard['handicap_coefficient'],
                scorecard['playing_handicap']
            ))
        
        # Eliminar tabla original y renombrar la temporal
        print(f"{Fore.YELLOW}Reemplazando tabla original...{Style.RESET_ALL}")
        cursor.execute("DROP TABLE scorecards")
        cursor.execute("ALTER TABLE scorecards_temp RENAME TO scorecards")
        
        # Confirmar cambios
        conn.commit()
        conn.close()
        
        print(f"{Fore.GREEN}Migración completada con éxito.{Style.RESET_ALL}")
        return True, f"Migración completada. Se actualizaron {len(scorecards)} tarjetas."
        
    except Exception as e:
        print(f"{Fore.RED}Error durante la migración: {str(e)}{Style.RESET_ALL}")
        # Intentar cerrar la conexión si está abierta
        try:
            conn.close()
        except:
            pass
        return False, f"Error durante la migración: {str(e)}"


def run_migrations(db_path):
    """
    Ejecuta todas las migraciones necesarias.
    
    Args:
        db_path (str): Ruta al archivo de base de datos
        
    Returns:
        bool: True si todas las migraciones se completaron con éxito
    """
    migrations = [
        ("Añadir campo handicap_strokes a tarjetas", migrate_scorecards_add_handicap_strokes)
    ]
    
    success = True
    
    for name, migration_func in migrations:
        print(f"\n{Fore.CYAN}Ejecutando migración: {name}{Style.RESET_ALL}")
        migration_success, message = migration_func(db_path)
        
        if not migration_success:
            print(f"{Fore.RED}La migración '{name}' falló: {message}{Style.RESET_ALL}")
            success = False
            break
        else:
            print(f"{Fore.GREEN}Migración '{name}' completada: {message}{Style.RESET_ALL}")
    
    if success:
        print(f"\n{Fore.GREEN}Todas las migraciones se completaron con éxito.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}Algunas migraciones fallaron. La base de datos puede estar en un estado inconsistente.{Style.RESET_ALL}")
    
    return success
