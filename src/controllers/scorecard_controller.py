from src.database import Database
from src.models.scorecard import Scorecard
from datetime import datetime
import json

class ScorecardController:
    """
    Controlador para gestionar operaciones relacionadas con tarjetas de puntuación.
    """
    
    def __init__(self, database=None):
        """
        Inicializa el controlador con una conexión a la base de datos.
        
        Args:
            database (Database, optional): Instancia de la base de datos
        """
        self.db = database or Database()
    
    def add_scorecard(self, player_id, course_id, date, strokes, points, handicap_coefficient, playing_handicap=None):
        """
        Añade una nueva tarjeta de puntuación.
        
        Args:
            player_id (int): ID del jugador
            course_id (int): ID del campo
            date (str): Fecha en formato YYYY-MM-DD
            strokes (list): Lista de golpes por hoyo
            points (list): Lista de puntos stableford por hoyo
            handicap_coefficient (int): Coeficiente de hándicap aplicado (como porcentaje)
            playing_handicap (float, optional): Hándicap de juego final
            
        Returns:
            int: ID de la tarjeta creada, o None si falla
        """
        try:
            # Validaciones
            if not player_id or not course_id:
                return False, "El jugador y el campo son obligatorios."
            
            # Verificar que el jugador existe
            player = self.db.get_player(player_id)
            if not player:
                return False, f"No se encontró ningún jugador con ID {player_id}."
            
            # Verificar que el campo existe
            course = self.db.get_course(course_id)
            if not course:
                return False, f"No se encontró ningún campo con ID {course_id}."
            
            # Validar fecha
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return False, "Formato de fecha inválido. Use YYYY-MM-DD."
            
            # Validar listas
            if not all(isinstance(s, int) for s in strokes):
                return False, "Los golpes deben ser números enteros."
                
            if not all(isinstance(p, int) for p in points):
                return False, "Los puntos deben ser números enteros."
            
            # Convertir listas a JSON
            strokes_json = json.dumps(strokes)
            points_json = json.dumps(points)
            
            # Añadir a la base de datos
            scorecard_id = self.db.add_scorecard(
                player_id, course_id, date, strokes_json, points_json, 
                handicap_coefficient, playing_handicap
            )
            
            if scorecard_id:
                return True, scorecard_id
            else:
                return False, "Error al guardar la tarjeta en la base de datos."
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_scorecard(self, scorecard_id):
        """
        Obtiene una tarjeta por su ID.
        
        Args:
            scorecard_id (int): ID de la tarjeta
            
        Returns:
            Scorecard: Instancia de la tarjeta o None si no existe
        """
        try:
            scorecard_data = self.db.get_scorecard_with_details(scorecard_id)
            if not scorecard_data:
                return None
            
            # Usar el método from_joined_row del modelo Scorecard
            return Scorecard.from_joined_row(scorecard_data)
            
        except Exception as e:
            print(f"Error al obtener tarjeta: {str(e)}")
            return None
    
    def get_scorecards(self, limit=50, offset=0):
        """
        Obtiene todas las tarjetas.
        
        Args:
            limit (int): Límite de resultados
            offset (int): Desplazamiento para paginación
            
        Returns:
            list: Lista de instancias de Scorecard
        """
        try:
            scorecards_data = self.db.get_scorecards(limit, offset)
            result = []
            
            for row in scorecards_data:
                try:
                    # Usar el método from_joined_row del modelo Scorecard
                    scorecard = Scorecard.from_joined_row(row)
                    result.append(scorecard)
                except Exception as e:
                    print(f"Error al procesar tarjeta: {str(e)}")
                    continue
            
            return result
            
        except Exception as e:
            print(f"Error al obtener tarjetas: {str(e)}")
            return []
    
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
            list: Lista de instancias de Scorecard
        """
        try:
            scorecards_data = self.db.search_scorecards(filters)
            result = []
            
            for row in scorecards_data:
                try:
                    # Convertir strings a listas, filtrando valores vacíos
                    strokes = [int(x) for x in row['strokes'].split(',') if x.strip()] if row['strokes'] else []
                    points = [int(x) for x in row['points'].split(',') if x.strip()] if row['points'] else []
                    
                    scorecard = Scorecard(
                        id=row['id'],
                        player_id=row['player_id'],
                        course_id=row['course_id'],
                        date=row['date'],
                        strokes=strokes,
                        points=points,
                        handicap_coefficient=row['handicap_coefficient'],
                        playing_handicap=row['playing_handicap'],
                        player_name=f"{row['first_name']} {row['surname']}",
                        course_name=row['name']
                    )
                    result.append(scorecard)
                except Exception as e:
                    print(f"Error al procesar tarjeta filtrada: {str(e)}")
                    continue
                
            return result
            
        except Exception as e:
            print(f"Error al filtrar tarjetas: {str(e)}")
            return []
    
    def delete_scorecard(self, scorecard_id):
        """
        Elimina una tarjeta.
        
        Args:
            scorecard_id (int): ID de la tarjeta a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            return self.db.delete_scorecard(scorecard_id)
        except Exception:
            return False
            
    def update_scorecard(self, scorecard_id, player_id=None, course_id=None, date=None, 
                         strokes=None, points=None, handicap_coefficient=None, playing_handicap=None):
        """
        Actualiza una tarjeta existente.
        
        Args:
            scorecard_id (int): ID de la tarjeta a actualizar
            player_id (int, optional): Nuevo ID de jugador
            course_id (int, optional): Nuevo ID de campo
            date (str, optional): Nueva fecha
            strokes (list, optional): Nueva lista de golpes
            points (list, optional): Nueva lista de puntos stableford
            handicap_coefficient (int, optional): Nuevo coeficiente de hándicap
            playing_handicap (float, optional): Nuevo hándicap de juego
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Obtener la tarjeta actual
            current = self.get_scorecard(scorecard_id)
            if not current:
                return False
            
            # Usar valores actuales si no se proporcionan nuevos
            player_id = player_id if player_id is not None else current.player_id
            course_id = course_id if course_id is not None else current.course_id
            date = date if date is not None else current.date
            strokes = strokes if strokes is not None else current.strokes
            points = points if points is not None else current.points
            handicap_coefficient = handicap_coefficient if handicap_coefficient is not None else current.handicap_coefficient
            playing_handicap = playing_handicap if playing_handicap is not None else current.playing_handicap
            
            # Convertir listas a JSON
            strokes_json = json.dumps(strokes)
            points_json = json.dumps(points)
            
            # Actualizar en la base de datos
            success = self.db.update_scorecard(
                scorecard_id, player_id, course_id, date, strokes_json, points_json,
                handicap_coefficient, playing_handicap
            )
            
            return success
        except Exception as e:
            print(f"Error al actualizar tarjeta: {e}")
            return False
            
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
        try:
            return self.db.get_stats(player_id, course_id, start_date, end_date)
        except Exception:
            return {
                'total_rounds': 0,
                'avg_strokes': 0,
                'best_round': 0,
                'worst_round': 0,
                'avg_points': 0
            }
