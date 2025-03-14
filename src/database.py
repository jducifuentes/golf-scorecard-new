import sqlite3
import os
from datetime import datetime
import json

class Database:
    """
    Clase para gestionar la conexión y operaciones con la base de datos SQLite.
    """
    
    def __init__(self, db_name='data/golf.db'):
        """
        Inicializa la conexión a la base de datos y crea las tablas si no existen.
        
        Args:
            db_name (str): Nombre del archivo de base de datos
        """
        # Determinar la ruta base del proyecto (directorio raíz)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Construir la ruta completa al archivo de base de datos
        self.db_path = os.path.join(base_dir, db_name)
        
        # Asegurar que el directorio data existe si se usa una ruta con subdirectorios
        if '/' in db_name or '\\' in db_name:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Conectar a la base de datos
        self.connection = sqlite3.connect(self.db_path)
        
        # Configurar para obtener filas como diccionarios
        self.connection.row_factory = sqlite3.Row
        
        # Crear las tablas si no existen
        self.create_tables()
    
    def create_tables(self):
        """Crea las tablas necesarias si no existen"""
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    handicap REAL NOT NULL
                )
            ''')
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    slope INTEGER NOT NULL,
                    course_rating REAL NOT NULL,
                    par_total INTEGER NOT NULL,
                    hole_pars TEXT NOT NULL,
                    hole_handicaps TEXT NOT NULL
                )
            ''')
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS scorecards (
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

    def reset_database(self):
        """Elimina todas las tablas y las vuelve a crear"""
        with self.connection:
            self.connection.execute('DROP TABLE IF EXISTS scorecards')
            self.connection.execute('DROP TABLE IF EXISTS players')
            self.connection.execute('DROP TABLE IF EXISTS courses')
        self.create_tables()
        return True

    # ===== Operaciones con Jugadores =====
    
    def add_player(self, first_name, surname, handicap):
        """Añade un nuevo jugador a la base de datos"""
        with self.connection:
            cursor = self.connection.execute('''
                INSERT INTO players (first_name, surname, handicap)
                VALUES (?, ?, ?)
            ''', (first_name, surname, handicap))
            return cursor.lastrowid

    def update_player(self, player_id, first_name, surname, handicap):
        """Actualiza los datos de un jugador existente"""
        with self.connection:
            self.connection.execute('''
                UPDATE players 
                SET first_name = ?, surname = ?, handicap = ?
                WHERE id = ?
            ''', (first_name, surname, handicap, player_id))
            return True

    def get_player(self, player_id):
        """Obtiene un jugador por su ID"""
        with self.connection:
            result = self.connection.execute(
                'SELECT * FROM players WHERE id = ?', 
                (player_id,)
            ).fetchone()
            return dict(result) if result else None

    def get_players(self):
        """Obtiene todos los jugadores"""
        with self.connection:
            return self.connection.execute('SELECT * FROM players ORDER BY surname, first_name').fetchall()

    def delete_player(self, player_id, delete_scorecards=False):
        """
        Elimina un jugador por su ID
        
        Args:
            player_id (int): ID del jugador a eliminar
            delete_scorecards (bool): Si es True, elimina también las tarjetas asociadas
            
        Returns:
            tuple: (éxito, mensaje)
        """
        with self.connection:
            # Primero verificar si hay tarjetas asociadas
            scorecards = self.connection.execute(
                'SELECT COUNT(*) FROM scorecards WHERE player_id = ?', 
                (player_id,)
            ).fetchone()[0]
            
            if scorecards > 0 and not delete_scorecards:
                return False, f"No se puede eliminar el jugador porque tiene {scorecards} tarjetas asociadas."
            
            # Si hay tarjetas y se ha indicado eliminarlas, eliminar primero las tarjetas
            if scorecards > 0 and delete_scorecards:
                self.connection.execute('DELETE FROM scorecards WHERE player_id = ?', (player_id,))
            
            # Eliminar el jugador
            self.connection.execute('DELETE FROM players WHERE id = ?', (player_id,))
            
            if delete_scorecards and scorecards > 0:
                return True, f"Jugador eliminado correctamente junto con {scorecards} tarjetas asociadas."
            else:
                return True, "Jugador eliminado correctamente."

    # ===== Operaciones con Campos =====
    
    def add_course(self, name, location, slope, course_rating, par_total, hole_pars, hole_handicaps):
        """Añade un nuevo campo a la base de datos"""
        # Convertir listas a formato JSON
        hole_pars_json = json.dumps(hole_pars)
        hole_handicaps_json = json.dumps(hole_handicaps)
        
        with self.connection:
            cursor = self.connection.execute('''
                INSERT INTO courses (name, location, slope, course_rating, par_total, hole_pars, hole_handicaps)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, location, slope, course_rating, par_total, hole_pars_json, hole_handicaps_json))
            return cursor.lastrowid

    def update_course(self, course_id, name, location, slope, course_rating, par_total, hole_pars, hole_handicaps):
        """Actualiza los datos de un campo existente"""
        # Convertir listas a formato JSON
        hole_pars_json = json.dumps(hole_pars)
        hole_handicaps_json = json.dumps(hole_handicaps)
        
        with self.connection:
            self.connection.execute('''
                UPDATE courses 
                SET name = ?, location = ?, slope = ?, course_rating = ?, 
                    par_total = ?, hole_pars = ?, hole_handicaps = ?
                WHERE id = ?
            ''', (name, location, slope, course_rating, par_total, 
                  hole_pars_json, hole_handicaps_json, course_id))
            return True

    def get_course(self, course_id):
        """Obtiene un campo por su ID"""
        with self.connection:
            result = self.connection.execute(
                'SELECT * FROM courses WHERE id = ?', 
                (course_id,)
            ).fetchone()
            return dict(result) if result else None

    def get_courses(self):
        """Obtiene todos los campos"""
        with self.connection:
            return self.connection.execute('SELECT * FROM courses ORDER BY name').fetchall()

    def delete_course(self, course_id, delete_scorecards=False):
        """
        Elimina un campo por su ID
        
        Args:
            course_id (int): ID del campo a eliminar
            delete_scorecards (bool): Si es True, elimina también las tarjetas asociadas
            
        Returns:
            tuple: (éxito, mensaje)
        """
        with self.connection:
            # Primero verificar si hay tarjetas asociadas
            scorecards = self.connection.execute(
                'SELECT COUNT(*) FROM scorecards WHERE course_id = ?', 
                (course_id,)
            ).fetchone()[0]
            
            if scorecards > 0 and not delete_scorecards:
                return False, f"No se puede eliminar el campo porque tiene {scorecards} tarjetas asociadas."
            
            # Si hay tarjetas y se ha indicado eliminarlas, eliminar primero las tarjetas
            if scorecards > 0 and delete_scorecards:
                self.connection.execute('DELETE FROM scorecards WHERE course_id = ?', (course_id,))
            
            # Eliminar el campo
            self.connection.execute('DELETE FROM courses WHERE id = ?', (course_id,))
            
            if delete_scorecards and scorecards > 0:
                return True, f"Campo eliminado correctamente junto con {scorecards} tarjetas asociadas."
            else:
                return True, "Campo eliminado correctamente."

    # ===== Operaciones con Tarjetas =====
    
    def add_scorecard(self, player_id, course_id, date, strokes, points, handicap_coefficient, playing_handicap=None, handicap_strokes=None):
        """
        Añade una nueva tarjeta a la base de datos.
        
        Args:
            player_id (int): ID del jugador
            course_id (int): ID del campo
            date (str): Fecha de la ronda en formato YYYY-MM-DD
            strokes (str): Golpes por hoyo en formato JSON
            points (str): Puntos por hoyo en formato JSON
            handicap_coefficient (float): Coeficiente de hándicap aplicado
            playing_handicap (float, optional): Hándicap de juego final
            handicap_strokes (str, optional): Golpes de hándicap por hoyo en formato JSON
            
        Returns:
            int: ID de la tarjeta creada o None si falla
        """
        try:
            # Validar datos
            if not player_id or not course_id or not date:
                return None
                
            # Preparar la consulta SQL
            query = """
                INSERT INTO scorecards (
                    player_id, course_id, date, strokes, handicap_strokes, points, 
                    handicap_coefficient, playing_handicap
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Ejecutar la consulta
            cursor = self.connection.cursor()
            cursor.execute(
                query, 
                (player_id, course_id, date, strokes, handicap_strokes, points, 
                 handicap_coefficient, playing_handicap)
            )
            
            # Obtener el ID de la tarjeta creada
            scorecard_id = cursor.lastrowid
            
            # Confirmar los cambios
            self.connection.commit()
            
            return scorecard_id
            
        except Exception as e:
            print(f"Error al añadir tarjeta: {e}")
            return None

    def get_scorecard(self, scorecard_id):
        """Obtiene una tarjeta por su ID"""
        with self.connection:
            result = self.connection.execute(
                'SELECT * FROM scorecards WHERE id = ?', 
                (scorecard_id,)
            ).fetchone()
            return dict(result) if result else None
    
    def get_scorecard_with_details(self, scorecard_id):
        """Obtiene una tarjeta con información de jugador y campo por su ID"""
        with self.connection:
            result = self.connection.execute('''
                SELECT s.*, p.first_name, p.surname, c.name, c.location, c.slope, c.course_rating, 
                       c.par_total, c.hole_pars, c.hole_handicaps
                FROM scorecards s
                LEFT JOIN players p ON s.player_id = p.id
                LEFT JOIN courses c ON s.course_id = c.id
                WHERE s.id = ?
            ''', (scorecard_id,)).fetchone()
            return result

    def get_scorecards(self, limit=50, offset=0):
        """Obtiene todas las tarjetas con información de jugador y campo"""
        with self.connection:
            return self.connection.execute('''
                SELECT s.*, p.first_name, p.surname, c.name, c.location, c.slope, c.course_rating, c.par_total, 
                       c.hole_pars, c.hole_handicaps
                FROM scorecards s
                LEFT JOIN players p ON s.player_id = p.id
                LEFT JOIN courses c ON s.course_id = c.id
                ORDER BY s.date DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset)).fetchall()

    def delete_scorecard(self, scorecard_id):
        """Elimina una tarjeta por su ID"""
        with self.connection:
            self.connection.execute('DELETE FROM scorecards WHERE id = ?', (scorecard_id,))
            return True

    def update_scorecard(self, scorecard_id, player_id, course_id, date, strokes, handicap_strokes, points,
                        handicap_coefficient, playing_handicap):
        """
        Actualiza una tarjeta existente.
        
        Args:
            scorecard_id (int): ID de la tarjeta a actualizar
            player_id (int): ID del jugador
            course_id (int): ID del campo
            date (str): Fecha de la ronda
            strokes (str): Golpes por hoyo en formato JSON
            handicap_strokes (str): Golpes de hándicap por hoyo en formato JSON
            points (str): Puntos por hoyo en formato JSON
            handicap_coefficient (float): Coeficiente de hándicap aplicado
            playing_handicap (float): Hándicap de juego final
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Preparar la consulta SQL
            query = """
                UPDATE scorecards
                SET player_id = ?, course_id = ?, date = ?, strokes = ?, handicap_strokes = ?, points = ?,
                    handicap_coefficient = ?, playing_handicap = ?
                WHERE id = ?
            """
            
            # Ejecutar la consulta
            cursor = self.connection.cursor()
            cursor.execute(
                query, 
                (player_id, course_id, date, strokes, handicap_strokes, points,
                 handicap_coefficient, playing_handicap, scorecard_id)
            )
            
            # Confirmar los cambios
            self.connection.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error al actualizar tarjeta: {e}")
            return False

    def search_scorecards(self, filters=None):
        """
        Busca tarjetas aplicando filtros.
        
        Args:
            filters (dict): Diccionario con los filtros a aplicar
                - player_id: ID del jugador
                - course_id: ID del campo
                - start_date: Fecha de inicio (YYYY-MM-DD)
                - end_date: Fecha de fin (YYYY-MM-DD)
                - player_name: Nombre parcial del jugador
                - course_name: Nombre parcial del campo
        
        Returns:
            list: Lista de tarjetas que cumplen los filtros
        """
        filters = filters or {}
        
        query = """
            SELECT s.*, p.first_name, p.surname, c.name, c.location, c.slope, c.course_rating, c.par_total, 
                   c.hole_pars, c.hole_handicaps
            FROM scorecards s
            LEFT JOIN players p ON s.player_id = p.id
            LEFT JOIN courses c ON s.course_id = c.id
            WHERE 1=1
        """
        params = []
        
        if 'player_id' in filters and filters['player_id']:
            query += " AND s.player_id = ?"
            params.append(filters['player_id'])
        
        if 'course_id' in filters and filters['course_id']:
            query += " AND s.course_id = ?"
            params.append(filters['course_id'])
        
        if 'start_date' in filters and filters['start_date']:
            query += " AND s.date >= ?"
            params.append(filters['start_date'])
        
        if 'end_date' in filters and filters['end_date']:
            query += " AND s.date <= ?"
            params.append(filters['end_date'])
        
        if 'player_name' in filters and filters['player_name']:
            query += " AND (p.first_name LIKE ? OR p.surname LIKE ?)"
            name_pattern = f"%{filters['player_name']}%"
            params.extend([name_pattern, name_pattern])
        
        if 'course_name' in filters and filters['course_name']:
            query += " AND c.name LIKE ?"
            params.append(f"%{filters['course_name']}%")
        
        query += " ORDER BY s.date DESC"
        
        with self.connection:
            return self.connection.execute(query, params).fetchall()

    def get_stats(self, player_id=None, course_id=None, start_date=None, end_date=None):
        """
        Obtiene estadísticas de las tarjetas.
        
        Args:
            player_id (int, optional): Filtrar por jugador
            course_id (int, optional): Filtrar por campo
            start_date (str, optional): Fecha de inicio (YYYY-MM-DD)
            end_date (str, optional): Fecha de fin (YYYY-MM-DD)
        
        Returns:
            dict: Diccionario con estadísticas
        """
        query = """
            SELECT 
                COUNT(*) as total_rounds,
                AVG(total_strokes) as avg_strokes,
                MIN(total_strokes) as best_round,
                MAX(total_strokes) as worst_round,
                AVG(total_points) as avg_points
            FROM (
                SELECT 
                    s.id,
                    SUM(CAST(value as INTEGER)) as total_strokes,
                    SUM(CAST(point as INTEGER)) as total_points
                FROM scorecards s
                JOIN players p ON s.player_id = p.id
                JOIN courses c ON s.course_id = c.id,
                json_each('["' || REPLACE(s.strokes, ',', '","') || '"]') as strokes(value),
                json_each('["' || REPLACE(s.points, ',', '","') || '"]') as points(point)
                WHERE 1=1
        """
        params = []
        
        if player_id:
            query += " AND s.player_id = ?"
            params.append(player_id)
        
        if course_id:
            query += " AND s.course_id = ?"
            params.append(course_id)
        
        if start_date:
            query += " AND s.date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND s.date <= ?"
            params.append(end_date)
        
        query += " GROUP BY s.id)"
        
        with self.connection:
            result = self.connection.execute(query, params).fetchone()
            return dict(result) if result else {
                'total_rounds': 0,
                'avg_strokes': 0,
                'best_round': 0,
                'worst_round': 0,
                'avg_points': 0
            }
