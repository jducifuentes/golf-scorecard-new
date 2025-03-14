"""
Controlador para gestionar las operaciones relacionadas con las tarjetas de puntuación.
"""
from datetime import datetime
import json
from src.database import Database
from src.models.scorecard import Scorecard


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
    
    def create_scorecard(self, player_id, course_id, date=None, strokes=None, 
                        playing_handicap=None, handicap_coefficient=100):
        """
        Crea una nueva tarjeta de puntuación.
        
        Args:
            player_id (int): ID del jugador
            course_id (int): ID del campo
            date (str, optional): Fecha en formato YYYY-MM-DD
            strokes (list, optional): Lista de golpes por hoyo
            playing_handicap (float, optional): Hándicap de juego
            handicap_coefficient (int, optional): Coeficiente de hándicap (%)
            
        Returns:
            tuple: (éxito, resultado/mensaje)
        """
        try:
            # Validaciones básicas
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
            if date:
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    return False, "Formato de fecha inválido. Use YYYY-MM-DD."
            else:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Inicializar listas
            strokes = strokes or []
            
            # Validar golpes
            if strokes and not all(isinstance(s, int) and s > 0 for s in strokes):
                return False, "Los golpes deben ser números enteros positivos."
            
            # Calcular puntos y golpes con hándicap
            points = []
            handicap_strokes = []
            
            if strokes and course:
                # Obtener los pares de cada hoyo y los hándicaps de cada hoyo
                hole_pars = json.loads(course['hole_pars']) if isinstance(course['hole_pars'], str) else course['hole_pars']
                hole_handicaps = json.loads(course['hole_handicaps']) if isinstance(course['hole_handicaps'], str) else course['hole_handicaps']
                
                # Si no se proporciona el hándicap de juego, calcularlo
                if playing_handicap is None and 'handicap' in player:
                    # Fórmula básica: handicap del jugador * (slope/113) * coeficiente
                    slope = course['slope']
                    player_handicap = player['handicap']
                    playing_handicap = round(player_handicap * (slope/113) * (handicap_coefficient/100), 1)
                
                # Calcular los golpes con hándicap y los puntos para cada hoyo
                for i, stroke in enumerate(strokes):
                    if i < len(hole_pars) and i < len(hole_handicaps):
                        par = hole_pars[i]
                        hole_handicap = hole_handicaps[i]
                        
                        # Calcular golpes extra por hándicap para este hoyo
                        extra_strokes = 0
                        if playing_handicap is not None:
                            # Distribuir el hándicap según la dificultad de los hoyos
                            if playing_handicap >= hole_handicap:
                                extra_strokes += 1
                            # Para hándicaps altos, se pueden asignar más de un golpe extra por hoyo
                            if playing_handicap >= hole_handicap + 18:
                                extra_strokes += 1
                            # Para hándicaps muy altos
                            if playing_handicap >= hole_handicap + 36:
                                extra_strokes += 1
                        
                        # Calcular golpes netos (con hándicap)
                        net_stroke = max(1, stroke - extra_strokes)
                        handicap_strokes.append(net_stroke)
                        
                        # Calcular puntos stableford
                        # 0 puntos: Más de 1 sobre par neto
                        # 1 punto: 1 sobre par neto (bogey)
                        # 2 puntos: Par neto
                        # 3 puntos: 1 bajo par neto (birdie)
                        # 4 puntos: 2 bajo par neto (eagle)
                        # 5 puntos: 3 bajo par neto (albatross)
                        if net_stroke > par + 1:
                            points.append(0)
                        elif net_stroke == par + 1:
                            points.append(1)
                        elif net_stroke == par:
                            points.append(2)
                        elif net_stroke == par - 1:
                            points.append(3)
                        elif net_stroke == par - 2:
                            points.append(4)
                        elif net_stroke <= par - 3:
                            points.append(5)
            
            # Convertir listas a JSON
            strokes_json = json.dumps(strokes)
            handicap_strokes_json = json.dumps(handicap_strokes)
            points_json = json.dumps(points)
            
            # Añadir a la base de datos
            scorecard_id = self.db.add_scorecard(
                player_id, course_id, date, strokes_json, 
                points_json, handicap_coefficient, playing_handicap,
                handicap_strokes_json
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
            
            return Scorecard.from_db_row(scorecard_data)
            
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
                    scorecard = Scorecard.from_db_row(row)
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
                    scorecard = Scorecard.from_db_row(row)
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
                         strokes=None, playing_handicap=None, handicap_coefficient=None):
        """
        Actualiza una tarjeta existente.
        
        Args:
            scorecard_id (int): ID de la tarjeta a actualizar
            player_id (int, optional): ID del jugador
            course_id (int, optional): ID del campo
            date (str, optional): Fecha de la ronda
            strokes (list, optional): Lista de golpes por hoyo
            playing_handicap (float, optional): Hándicap de juego
            handicap_coefficient (int, optional): Coeficiente de hándicap (%)
            
        Returns:
            tuple: (éxito, resultado/mensaje)
        """
        try:
            # Obtener la tarjeta actual
            current_scorecard = self.get_scorecard(scorecard_id)
            if not current_scorecard:
                return False, f"No se encontró ninguna tarjeta con ID {scorecard_id}."
            
            # Usar valores actuales si no se proporcionan nuevos
            player_id = player_id or current_scorecard.player_id
            course_id = course_id or current_scorecard.course_id
            date = date or current_scorecard.date
            strokes = strokes if strokes is not None else current_scorecard.strokes
            playing_handicap = playing_handicap if playing_handicap is not None else current_scorecard.playing_handicap
            handicap_coefficient = handicap_coefficient if handicap_coefficient is not None else current_scorecard.handicap_coefficient
            
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
            
            # Validar golpes
            if not all(isinstance(s, int) and s > 0 for s in strokes):
                return False, "Los golpes deben ser números enteros positivos."
            
            # Calcular puntos y golpes con hándicap
            points = []
            handicap_strokes = []
            
            # Obtener los pares de cada hoyo y los hándicaps de cada hoyo
            hole_pars = json.loads(course['hole_pars']) if isinstance(course['hole_pars'], str) else course['hole_pars']
            hole_handicaps = json.loads(course['hole_handicaps']) if isinstance(course['hole_handicaps'], str) else course['hole_handicaps']
            
            # Calcular los golpes con hándicap y los puntos para cada hoyo
            for i, stroke in enumerate(strokes):
                if i < len(hole_pars) and i < len(hole_handicaps):
                    par = hole_pars[i]
                    hole_handicap = hole_handicaps[i]
                    
                    # Calcular golpes extra por hándicap para este hoyo
                    extra_strokes = 0
                    if playing_handicap is not None:
                        # Distribuir el hándicap según la dificultad de los hoyos
                        if playing_handicap >= hole_handicap:
                            extra_strokes += 1
                        # Para hándicaps altos, se pueden asignar más de un golpe extra por hoyo
                        if playing_handicap >= hole_handicap + 18:
                            extra_strokes += 1
                        # Para hándicaps muy altos
                        if playing_handicap >= hole_handicap + 36:
                            extra_strokes += 1
                    
                    # Calcular golpes netos (con hándicap)
                    net_stroke = max(1, stroke - extra_strokes)
                    handicap_strokes.append(net_stroke)
                    
                    # Calcular puntos stableford
                    if net_stroke > par + 1:
                        points.append(0)
                    elif net_stroke == par + 1:
                        points.append(1)
                    elif net_stroke == par:
                        points.append(2)
                    elif net_stroke == par - 1:
                        points.append(3)
                    elif net_stroke == par - 2:
                        points.append(4)
                    elif net_stroke <= par - 3:
                        points.append(5)
            
            # Convertir listas a JSON
            strokes_json = json.dumps(strokes)
            handicap_strokes_json = json.dumps(handicap_strokes)
            points_json = json.dumps(points)
            
            # Actualizar en la base de datos
            success = self.db.update_scorecard(
                scorecard_id, player_id, course_id, date, 
                strokes_json, handicap_strokes_json, points_json,
                handicap_coefficient, playing_handicap
            )
            
            if success:
                return True, "Tarjeta actualizada correctamente."
            else:
                return False, "Error al actualizar la tarjeta en la base de datos."
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def calculate_scorecard_stats(self, scorecard):
        """
        Calcula estadísticas para una tarjeta.
        
        Args:
            scorecard (Scorecard): Tarjeta de puntuación
            
        Returns:
            dict: Diccionario con estadísticas
        """
        try:
            # Obtener datos del campo
            course = self.db.get_course(scorecard.course_id)
            if not course:
                return {}
            
            # Convertir datos del campo
            hole_pars = json.loads(course['hole_pars']) if isinstance(course['hole_pars'], str) else course['hole_pars']
            
            # Inicializar estadísticas
            stats = {
                'total_strokes': scorecard.total_strokes(),
                'total_handicap_strokes': scorecard.total_handicap_strokes(),
                'total_points': scorecard.total_points(),
                'par_total': course['par_total'],
                'vs_par': scorecard.total_strokes() - course['par_total'],
                'vs_handicap_par': scorecard.total_handicap_strokes() - course['par_total'],
                'holes_played': len(scorecard.strokes),
                'pars': 0,
                'birdies': 0,
                'eagles': 0,
                'bogeys': 0,
                'double_bogeys': 0,
                'others': 0
            }
            
            # Calcular estadísticas por hoyo
            for i, stroke in enumerate(scorecard.strokes):
                if i < len(hole_pars):
                    par = hole_pars[i]
                    diff = stroke - par
                    
                    if diff == 0:
                        stats['pars'] += 1
                    elif diff == -1:
                        stats['birdies'] += 1
                    elif diff <= -2:
                        stats['eagles'] += 1
                    elif diff == 1:
                        stats['bogeys'] += 1
                    elif diff == 2:
                        stats['double_bogeys'] += 1
                    else:
                        stats['others'] += 1
            
            return stats
            
        except Exception as e:
            print(f"Error al calcular estadísticas: {str(e)}")
            return {}
