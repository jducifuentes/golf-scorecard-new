"""
Utilidades para la vista de tarjetas de puntuación.
"""
from src.controllers.player_controller import PlayerController
from src.controllers.course_controller import CourseController

class ScorecardUtils:
    """
    Utilidades para la vista de tarjetas de puntuación.
    """
    
    @staticmethod
    def get_player_name(scorecard, player=None, player_controller=None):
        """
        Obtiene el nombre del jugador de una tarjeta.
        
        Args:
            scorecard: La tarjeta de puntuación
            player: El jugador (opcional)
            player_controller: Controlador de jugadores (opcional)
            
        Returns:
            str: El nombre del jugador
        """
        if hasattr(scorecard, 'player_name') and scorecard.player_name:
            return scorecard.player_name
        
        if player is None and player_controller:
            player = player_controller.get_player(scorecard.player_id)
        
        return f"{player.first_name} {player.surname}" if player else "Jugador desconocido"
    
    @staticmethod
    def get_course_name(scorecard, course=None, course_controller=None):
        """
        Obtiene el nombre del campo de una tarjeta.
        
        Args:
            scorecard: La tarjeta de puntuación
            course: El campo (opcional)
            course_controller: Controlador de campos (opcional)
            
        Returns:
            str: El nombre del campo
        """
        if hasattr(scorecard, 'course_name') and scorecard.course_name:
            return scorecard.course_name
        
        if course is None and course_controller:
            course = course_controller.get_course(scorecard.course_id)
        
        return course.name if course else "Desconocido"
    
    @staticmethod
    def format_date(date_str):
        """
        Formatea una fecha de YYYY-MM-DD a DD/MM/YYYY.
        
        Args:
            date_str: La fecha en formato YYYY-MM-DD
            
        Returns:
            str: La fecha formateada
        """
        if date_str and isinstance(date_str, str):
            try:
                year, month, day = date_str.split('-')
                return f"{day}/{month}/{year}"
            except ValueError:
                return date_str
        return str(date_str)
    
    @staticmethod
    def calculate_total_strokes(scorecard):
        """
        Calcula el total de golpes de una tarjeta de forma segura.
        
        Args:
            scorecard: La tarjeta de puntuación
            
        Returns:
            int: El total de golpes
        """
        try:
            return sum(scorecard.strokes) if hasattr(scorecard, 'strokes') and scorecard.strokes else 0
        except Exception as e:
            print(f"Error al calcular golpes: {e}")
            return 0
    
    @staticmethod
    def calculate_total_points(scorecard):
        """
        Calcula el total de puntos de una tarjeta de forma segura.
        
        Args:
            scorecard: La tarjeta de puntuación
            
        Returns:
            int: El total de puntos
        """
        try:
            return sum(scorecard.points) if hasattr(scorecard, 'points') and scorecard.points else 0
        except Exception as e:
            print(f"Error al calcular puntos: {e}")
            return 0
    
    @staticmethod
    def calculate_result_string(total_strokes, course):
        """
        Calcula la cadena de resultado respecto al par.
        
        Args:
            total_strokes: El total de golpes
            course: El campo
            
        Returns:
            str: La cadena de resultado
        """
        if not total_strokes:
            return "N/A"
            
        if course and hasattr(course, 'par_total') and course.par_total:
            try:
                result = total_strokes - course.par_total
                return f"{result:+d}" if result != 0 else "E"
            except Exception as e:
                print(f"Error al calcular resultado: {e}")
                return "N/A"
        return "N/A"
    
    @staticmethod
    def prepare_scorecard_data(scorecard, player_controller=None, course_controller=None, player=None, course=None):
        """
        Prepara los datos de una tarjeta para su visualización.
        
        Args:
            scorecard (Scorecard): Tarjeta a preparar
            player_controller (PlayerController, optional): Controlador de jugadores
            course_controller (CourseController, optional): Controlador de campos
            player (Player, optional): Jugador (si ya se ha obtenido)
            course (Course, optional): Campo (si ya se ha obtenido)
            
        Returns:
            dict: Datos preparados para visualización
        """
        data = {
            'id': scorecard.id,
            'date': scorecard.date,
            'player_id': scorecard.player_id,
            'course_id': scorecard.course_id,
            'player_name': 'Desconocido',
            'course_name': 'Desconocido',
            'total_strokes': sum(scorecard.strokes) if scorecard.strokes else 0,
            'total_points': sum(scorecard.points) if scorecard.points else 0,
            'result_str': '',
            'handicap_coefficient': scorecard.handicap_coefficient
        }
        
        # Obtener jugador si no se proporciona
        if not player and player_controller and scorecard.player_id:
            player = player_controller.get_player(scorecard.player_id)
            
        # Obtener campo si no se proporciona
        if not course and course_controller and scorecard.course_id:
            course = course_controller.get_course(scorecard.course_id)
            
        # Añadir datos del jugador si está disponible
        if player:
            data['player_name'] = f"{player.first_name} {player.surname}"
            
        # Añadir datos del campo si está disponible
        if course:
            data['course_name'] = course.name
            data['course_location'] = course.location
            
            # Calcular resultado en relación al par
            if hasattr(course, 'par') and course.par and scorecard.strokes:
                total_par = course.par
                total_strokes = sum(scorecard.strokes)
                diff = total_strokes - total_par
                
                if diff < 0:
                    data['result_str'] = f"{abs(diff)} bajo par"
                elif diff == 0:
                    data['result_str'] = "Par"
                else:
                    data['result_str'] = f"{diff} sobre par"
        
        return data
