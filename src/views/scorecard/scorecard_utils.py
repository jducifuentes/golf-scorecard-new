"""
Utilidades para la visualización y manipulación de tarjetas de puntuación.
"""
from colorama import Fore, Style


class ScorecardUtils:
    """
    Clase de utilidades para tarjetas de puntuación.
    """
    
    @staticmethod
    def prepare_scorecard_data(scorecard, player_controller=None, course_controller=None, player=None, course=None):
        """
        Prepara los datos de una tarjeta para su visualización.
        
        Args:
            scorecard (Scorecard): Tarjeta de puntuación
            player_controller (PlayerController, optional): Controlador de jugadores
            course_controller (CourseController, optional): Controlador de campos
            player (Player, optional): Jugador (si ya se ha obtenido)
            course (Course, optional): Campo (si ya se ha obtenido)
            
        Returns:
            dict: Diccionario con los datos preparados
        """
        # Inicializar datos
        data = {
            'id': scorecard.id,
            'date': scorecard.date,
            'player_id': scorecard.player_id,
            'course_id': scorecard.course_id,
            'player_name': scorecard.player_name,
            'course_name': scorecard.course_name,
            'strokes': scorecard.strokes,
            'handicap_strokes': scorecard.handicap_strokes,
            'points': scorecard.points,
            'playing_handicap': scorecard.playing_handicap,
            'handicap_coefficient': scorecard.handicap_coefficient,
            'total_strokes': scorecard.total_strokes(),
            'total_handicap_strokes': scorecard.total_handicap_strokes(),
            'total_points': scorecard.total_points(),
            'holes_data': []
        }
        
        # Obtener jugador si no se proporciona
        if not player and player_controller and scorecard.player_id:
            player = player_controller.get_player(scorecard.player_id)
            if player:
                data['player_name'] = f"{player.first_name} {player.surname}"
                data['player_handicap'] = player.handicap
        
        # Obtener campo si no se proporciona
        if not course and course_controller and scorecard.course_id:
            course = course_controller.get_course(scorecard.course_id)
            if course:
                data['course_name'] = course.name
                data['course_location'] = course.location
                data['course_slope'] = course.slope
                data['course_rating'] = course.course_rating
                data['course_par_total'] = course.par_total
                data['course_hole_pars'] = course.hole_pars
                data['course_hole_handicaps'] = course.hole_handicaps
        
        # Añadir datos del campo desde el objeto course si está disponible
        if course:
            data['course_name'] = course.name
            data['course_location'] = course.location
            data['course_slope'] = course.slope
            data['course_rating'] = course.course_rating
            data['course_par_total'] = course.par_total
            data['course_hole_pars'] = course.hole_pars
            data['course_hole_handicaps'] = course.hole_handicaps
            
            # Calcular diferencia con el par
            if data.get('total_strokes') is not None and course.par_total:
                data['vs_par'] = data['total_strokes'] - course.par_total
                data['vs_par_text'] = ScorecardUtils.format_vs_par(data['vs_par'])
            
            # Calcular diferencia con el par neto
            if data.get('total_handicap_strokes') is not None and course.par_total:
                data['vs_handicap_par'] = data['total_handicap_strokes'] - course.par_total
                data['vs_handicap_par_text'] = ScorecardUtils.format_vs_par(data['vs_handicap_par'])
        
        # Preparar datos por hoyo
        hole_results = scorecard.get_all_holes_results()
        data['holes_data'] = hole_results
        
        return data
    
    @staticmethod
    def format_vs_par(value):
        """
        Formatea un valor de diferencia con el par.
        
        Args:
            value (int): Valor de diferencia con el par
            
        Returns:
            str: Texto formateado
        """
        if value == 0:
            return "E"
        elif value > 0:
            return f"+{value}"
        else:
            return str(value)
    
    @staticmethod
    def format_stroke_result(stroke, par):
        """
        Formatea un resultado de golpes para mostrar con color.
        
        Args:
            stroke (int): Golpes
            par (int): Par del hoyo
            
        Returns:
            str: Texto formateado con color
        """
        if stroke is None or par is None:
            return "-"
        
        diff = stroke - par
        result = str(stroke)
        
        if diff <= -2:
            # Eagle o mejor
            return f"{Fore.MAGENTA}{result}{Style.RESET_ALL}"
        elif diff == -1:
            # Birdie
            return f"{Fore.RED}{result}{Style.RESET_ALL}"
        elif diff == 0:
            # Par
            return f"{Fore.GREEN}{result}{Style.RESET_ALL}"
        elif diff == 1:
            # Bogey
            return f"{Fore.YELLOW}{result}{Style.RESET_ALL}"
        elif diff == 2:
            # Doble bogey
            return f"{Fore.BLUE}{result}{Style.RESET_ALL}"
        else:
            # Triple bogey o peor
            return f"{Fore.WHITE}{result}{Style.RESET_ALL}"
    
    @staticmethod
    def format_points(points):
        """
        Formatea los puntos stableford para mostrar con color.
        
        Args:
            points (int): Puntos
            
        Returns:
            str: Texto formateado con color
        """
        if points is None:
            return "-"
        
        result = str(points)
        
        if points >= 4:
            # Eagle o mejor
            return f"{Fore.MAGENTA}{result}{Style.RESET_ALL}"
        elif points == 3:
            # Birdie
            return f"{Fore.RED}{result}{Style.RESET_ALL}"
        elif points == 2:
            # Par
            return f"{Fore.GREEN}{result}{Style.RESET_ALL}"
        elif points == 1:
            # Bogey
            return f"{Fore.YELLOW}{result}{Style.RESET_ALL}"
        else:
            # No puntos
            return f"{Fore.WHITE}{result}{Style.RESET_ALL}"
    
    @staticmethod
    def get_score_name(stroke, par):
        """
        Obtiene el nombre del resultado según la diferencia con el par.
        
        Args:
            stroke (int): Golpes
            par (int): Par del hoyo
            
        Returns:
            str: Nombre del resultado
        """
        if stroke is None or par is None:
            return "-"
        
        diff = stroke - par
        
        if diff <= -3:
            return "Albatross o mejor"
        elif diff == -2:
            return "Eagle"
        elif diff == -1:
            return "Birdie"
        elif diff == 0:
            return "Par"
        elif diff == 1:
            return "Bogey"
        elif diff == 2:
            return "Doble Bogey"
        else:
            return "Triple Bogey o peor"
    
    @staticmethod
    def calculate_stats(scorecard, course=None):
        """
        Calcula estadísticas para una tarjeta.
        
        Args:
            scorecard (Scorecard): Tarjeta de puntuación
            course (Course, optional): Campo
            
        Returns:
            dict: Diccionario con estadísticas
        """
        stats = {
            'total_strokes': scorecard.total_strokes(),
            'total_handicap_strokes': scorecard.total_handicap_strokes(),
            'total_points': scorecard.total_points(),
            'holes_played': len(scorecard.strokes),
            'pars': 0,
            'birdies': 0,
            'eagles': 0,
            'bogeys': 0,
            'double_bogeys': 0,
            'others': 0
        }
        
        # Si no hay información del campo, no podemos calcular algunas estadísticas
        if not course:
            return stats
        
        # Añadir información del campo
        stats['par_total'] = course.par_total
        stats['vs_par'] = stats['total_strokes'] - course.par_total
        stats['vs_handicap_par'] = stats['total_handicap_strokes'] - course.par_total
        
        # Calcular estadísticas por hoyo
        hole_pars = course.hole_pars
        
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
