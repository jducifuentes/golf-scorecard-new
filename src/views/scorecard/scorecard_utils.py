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
            scorecard: Tarjeta a preparar
            player_controller: Controlador de jugadores
            course_controller: Controlador de campos
            player: Objeto jugador (opcional, si ya se ha obtenido)
            course: Objeto campo (opcional, si ya se ha obtenido)
            
        Returns:
            dict: Diccionario con los datos preparados
        """
        data = {
            'total_strokes': scorecard.total_strokes(),
            'total_points': scorecard.total_points() if hasattr(scorecard, 'total_points') else 0,
        }
        
        # Obtener jugador y campo si no se proporcionaron
        if not player and player_controller and scorecard.player_id:
            player = player_controller.get_player(scorecard.player_id)
        
        if not course and course_controller and scorecard.course_id:
            course = course_controller.get_course(scorecard.course_id)
        
        # Añadir información del jugador
        if player:
            data['player'] = player
            data['player_name'] = f"{player.first_name} {player.surname}"
            data['player_handicap'] = player.handicap
        else:
            data['player_name'] = f"Jugador #{scorecard.player_id}"
            data['player_handicap'] = "N/A"
        
        # Añadir información del campo
        if course:
            data['course'] = course
            data['course_name'] = course.name
            data['course_par'] = course.par_total
            
            # Calcular diferencia con el par
            data['vs_par'] = data['total_strokes'] - course.par_total
            if data['vs_par'] > 0:
                data['vs_par_text'] = f"+{data['vs_par']}"
            elif data['vs_par'] == 0:
                data['vs_par_text'] = "E (Par)"
            else:
                data['vs_par_text'] = f"{data['vs_par']}"
            
            # Calcular golpes netos totales
            if hasattr(scorecard, 'total_handicap_strokes'):
                data['total_handicap_strokes'] = scorecard.total_handicap_strokes()
                data['vs_handicap_par'] = data['total_handicap_strokes'] - course.par_total
                if data['vs_handicap_par'] > 0:
                    data['vs_handicap_par_text'] = f"+{data['vs_handicap_par']}"
                elif data['vs_handicap_par'] == 0:
                    data['vs_handicap_par_text'] = "E (Par)"
                else:
                    data['vs_handicap_par_text'] = f"{data['vs_handicap_par']}"
            else:
                data['total_handicap_strokes'] = "N/A"
        else:
            data['course_name'] = f"Campo #{scorecard.course_id}"
            data['course_par'] = "N/A"
        
        return data
    
    @staticmethod
    def format_stroke_result(strokes, par, playing_handicap=None, hole_handicap=None):
        """
        Formatea el resultado de golpes con colores según el par y hándicap.
        
        Args:
            strokes: Número de golpes
            par: Par del hoyo
            playing_handicap: Hándicap de juego del jugador
            hole_handicap: Hándicap del hoyo
            
        Returns:
            str: Texto formateado con colores
        """
        if strokes is None:
            return "-"
        
        if par is None:
            return str(strokes)
        
        # Calcular golpes extra por hándicap para este hoyo (no se usan en esta función)
        extra_strokes = 0
        if playing_handicap is not None and hole_handicap is not None:
            # Distribuir el hándicap según la dificultad de los hoyos
            if playing_handicap >= hole_handicap:
                extra_strokes += 1
            # Para hándicaps altos, se pueden asignar más de un golpe extra por hoyo
            if playing_handicap >= hole_handicap + 18:
                extra_strokes += 1
            # Para hándicaps muy altos (36+), se pueden asignar hasta 3 golpes extra
            if playing_handicap >= hole_handicap + 36:
                extra_strokes += 1
        
        # Calcular diferencia con el par
        diff = strokes - par
        
        # Formatear con colores según el resultado
        if diff < 0:  # Bajo par
            return f"{Fore.LIGHTBLUE_EX}{strokes}{Style.RESET_ALL}"
        elif diff == 0:  # Par
            return f"{Fore.LIGHTCYAN_EX}{strokes}{Style.RESET_ALL}"
        elif diff == 1:  # Bogey
            return f"{Fore.GREEN}{strokes}{Style.RESET_ALL}"
        elif diff == 2:  # Doble Bogey
            return f"{Fore.YELLOW}{strokes}{Style.RESET_ALL}"
        else:  # Triple Bogey o peor
            return f"{Fore.RED}{strokes}{Style.RESET_ALL}"
    
    @staticmethod
    def format_points(points):
        """
        Formatea los puntos con colores.
        
        Args:
            points: Puntos obtenidos
            
        Returns:
            str: Texto formateado con colores
        """
        if points is None:
            return "-"
        
        # Formatear con colores según los puntos
        if points == 0:  # 0 puntos
            return f"{Fore.RED}{points}{Style.RESET_ALL}"
        elif points == 1:  # 1 punto
            return f"{Fore.GREEN}{points}{Style.RESET_ALL}"
        elif points == 2:  # 2 puntos
            return f"{Fore.BLUE}{points}{Style.RESET_ALL}"
        elif points == 3:  # 3 puntos
            return f"{Fore.CYAN}{points}{Style.RESET_ALL}"
        elif points == 4:  # 4 puntos
            return f"{Fore.LIGHTYELLOW_EX}{points}{Style.RESET_ALL}"
        else:  # 5 o más puntos
            return f"{Fore.YELLOW}{points}{Style.RESET_ALL}"
    
    @staticmethod
    def get_score_name(strokes, par):
        """
        Obtiene el nombre del resultado según los golpes y el par.
        
        Args:
            strokes: Número de golpes
            par: Par del hoyo
            
        Returns:
            str: Nombre del resultado
        """
        if strokes is None or par is None:
            return "-"
        
        diff = strokes - par
        
        if diff <= -3:
            return "Albatros o mejor"
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
        elif diff == 3:
            return "Triple Bogey"
        else:
            return f"{diff} sobre par"
    
    @staticmethod
    def calculate_scratch_points(strokes, par):
        """
        Calcula los puntos Stableford sin aplicar hándicap (scratch).
        
        Args:
            strokes: Número de golpes
            par: Par del hoyo
            
        Returns:
            int: Puntos Stableford
        """
        if strokes is None or par is None:
            return 0
            
        # Calcular diferencia con el par
        diff = strokes - par
        
        # Calcular puntos según el sistema Stableford
        if diff <= -2:  # Eagle o mejor
            return 4
        elif diff == -1:  # Birdie
            return 3
        elif diff == 0:  # Par
            return 2
        elif diff == 1:  # Bogey
            return 1
        else:  # Doble bogey o peor
            return 0

    @staticmethod
    def calculate_stats(scorecard, course=None):
        """
        Calcula estadísticas para una tarjeta.
        
        Args:
            scorecard: Tarjeta de puntuación
            course: Campo
            
        Returns:
            dict: Diccionario con estadísticas
        """
        stats = {
            'total_strokes': scorecard.total_strokes(),
            'total_handicap_strokes': scorecard.total_handicap_strokes() if hasattr(scorecard, 'total_handicap_strokes') else 0,
            'total_points': scorecard.total_points() if hasattr(scorecard, 'total_points') else 0,
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
