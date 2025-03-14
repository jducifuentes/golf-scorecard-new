"""
Vista para mostrar estadísticas de tarjetas de puntuación.
"""
from colorama import Fore, Style
from src.controllers.scorecard_controller import ScorecardController
from src.controllers.player_controller import PlayerController
from src.controllers.course_controller import CourseController
from src.utils.formatters import (
    format_title, format_subtitle, format_table, format_info, 
    format_menu_option
)
from src.utils.helpers_simple import (
    clear_screen, pause, get_number_input
)
from src.views.scorecard.scorecard_utils import ScorecardUtils
from src.views.player_view import PlayerView
from src.views.course_view import CourseView

class ScorecardStatsView:
    """
    Vista para mostrar estadísticas de tarjetas de puntuación.
    """
    
    def __init__(self, controller=None, player_controller=None, course_controller=None):
        """
        Inicializa la vista con controladores.
        
        Args:
            controller (ScorecardController, optional): Controlador de tarjetas
            player_controller (PlayerController, optional): Controlador de jugadores
            course_controller (CourseController, optional): Controlador de campos
        """
        self.controller = controller or ScorecardController()
        self.player_controller = player_controller or PlayerController()
        self.course_controller = course_controller or CourseController()
        self.player_view = PlayerView(self.player_controller)
        self.course_view = CourseView(self.course_controller)
    
    def show_statistics(self):
        """
        Muestra estadísticas de tarjetas.
        """
        clear_screen()
        print(format_title("ESTADÍSTICAS DE TARJETAS"))
        
        print(format_menu_option("1", "Estadísticas por jugador"))
        print(format_menu_option("2", "Estadísticas por campo"))
        print(format_menu_option("3", "Mejores resultados"))
        print(format_menu_option("4", "Evolución de hándicap"))
        print(format_menu_option("0", "Volver"))
        
        option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=4, allow_float=False)
        
        if option == 0:
            # Volver al menú principal
            return
        elif option == 1:
            self._show_player_stats()
        elif option == 2:
            self._show_course_stats()
        elif option == 3:
            self._show_best_results()
        elif option == 4:
            self._show_handicap_evolution()
    
    def _show_player_stats(self):
        """
        Muestra estadísticas por jugador.
        """
        clear_screen()
        print(format_title("ESTADÍSTICAS POR JUGADOR"))
        
        # Seleccionar jugador
        print(format_subtitle("Seleccionar jugador"))
        player_id = self.player_view.select_player()
        if player_id is None:
            self.show_statistics()
            return
        
        player = self.player_controller.get_player(player_id)
        if not player:
            print(format_info("No se pudo obtener la información del jugador."))
            pause()
            self.show_statistics()
            return
        
        # Obtener tarjetas del jugador
        scorecards = self.controller.get_scorecards()
        player_scorecards = [sc for sc in scorecards if sc.player_id == player_id]
        
        if not player_scorecards:
            print(format_info(f"No hay tarjetas registradas para {player.first_name} {player.surname}."))
            pause()
            self.show_statistics()
            return
        
        # Preparar datos para estadísticas
        scorecard_data_list = []
        for sc in player_scorecards:
            course = self.course_controller.get_course(sc.course_id)
            if not course:
                continue
            
            scorecard_data = ScorecardUtils.prepare_scorecard_data(
                sc, self.player_controller, self.course_controller, player, course
            )
            
            # Añadir información para estadísticas
            scorecard_data['par_diff'] = scorecard_data['total_strokes'] - course.par_total
            scorecard_data['scorecard'] = sc
            
            scorecard_data_list.append(scorecard_data)
        
        # Calcular estadísticas
        total_rounds = len(scorecard_data_list)
        avg_strokes = sum(data['total_strokes'] for data in scorecard_data_list) / total_rounds if total_rounds > 0 else 0
        avg_points = sum(data['total_points'] for data in scorecard_data_list) / total_rounds if total_rounds > 0 else 0
        avg_par_diff = sum(data['par_diff'] for data in scorecard_data_list) / total_rounds if total_rounds > 0 else 0
        
        # Encontrar mejores y peores resultados
        if scorecard_data_list:
            best_result = min(scorecard_data_list, key=lambda x: x['par_diff'])
            worst_result = max(scorecard_data_list, key=lambda x: x['par_diff'])
            best_points = max(scorecard_data_list, key=lambda x: x['total_points'])
            worst_points = min(scorecard_data_list, key=lambda x: x['total_points'])
        else:
            best_result = worst_result = best_points = worst_points = None
        
        # Mostrar estadísticas
        print(format_subtitle(f"Estadísticas de {player.first_name} {player.surname}"))
        print(f"Hándicap actual: {player.handicap}")
        print(f"Total de rondas: {total_rounds}")
        print(f"Media de golpes: {avg_strokes:.1f}")
        print(f"Media respecto al par: {avg_par_diff:+.1f}")
        print(f"Media de puntos stableford: {avg_points:.1f}")
        
        if best_result:
            print(format_subtitle("Mejor resultado (golpes)"))
            print(f"Fecha: {best_result['date']}")
            print(f"Campo: {best_result['course_name']}")
            print(f"Golpes: {best_result['total_strokes']}")
            print(f"Resultado: {best_result['result_str']}")
            
            print(format_subtitle("Peor resultado (golpes)"))
            print(f"Fecha: {worst_result['date']}")
            print(f"Campo: {worst_result['course_name']}")
            print(f"Golpes: {worst_result['total_strokes']}")
            print(f"Resultado: {worst_result['result_str']}")
            
            print(format_subtitle("Mejor resultado (stableford)"))
            print(f"Fecha: {best_points['date']}")
            print(f"Campo: {best_points['course_name']}")
            print(f"Puntos stableford: {best_points['total_points']}")
            
            print(format_subtitle("Peor resultado (stableford)"))
            print(f"Fecha: {worst_points['date']}")
            print(f"Campo: {worst_points['course_name']}")
            print(f"Puntos stableford: {worst_points['total_points']}")
        
        pause()
        self.show_statistics()
    
    def _show_course_stats(self):
        """
        Muestra estadísticas por campo.
        """
        clear_screen()
        print(format_title("ESTADÍSTICAS POR CAMPO"))
        
        # Seleccionar campo
        print(format_subtitle("Seleccionar campo"))
        course_id = self.course_view.select_course()
        if course_id is None:
            self.show_statistics()
            return
        
        course = self.course_controller.get_course(course_id)
        if not course:
            print(format_info("No se pudo obtener la información del campo."))
            pause()
            self.show_statistics()
            return
        
        # Obtener tarjetas del campo
        scorecards = self.controller.get_scorecards()
        course_scorecards = [sc for sc in scorecards if sc.course_id == course_id]
        
        if not course_scorecards:
            print(format_info(f"No hay tarjetas registradas para el campo {course.name}."))
            pause()
            self.show_statistics()
            return
        
        # Preparar datos para estadísticas
        scorecard_data_list = []
        for sc in course_scorecards:
            player = self.player_controller.get_player(sc.player_id)
            if not player:
                continue
            
            scorecard_data = ScorecardUtils.prepare_scorecard_data(
                sc, self.player_controller, self.course_controller, player, course
            )
            
            # Añadir información para estadísticas
            scorecard_data['par_diff'] = scorecard_data['total_strokes'] - course.par_total
            scorecard_data['scorecard'] = sc
            
            scorecard_data_list.append(scorecard_data)
        
        # Calcular estadísticas
        total_rounds = len(scorecard_data_list)
        avg_strokes = sum(data['total_strokes'] for data in scorecard_data_list) / total_rounds if total_rounds > 0 else 0
        avg_points = sum(data['total_points'] for data in scorecard_data_list) / total_rounds if total_rounds > 0 else 0
        avg_par_diff = sum(data['par_diff'] for data in scorecard_data_list) / total_rounds if total_rounds > 0 else 0
        
        # Encontrar mejor y peor resultado
        if scorecard_data_list:
            best_result = min(scorecard_data_list, key=lambda x: x['par_diff'])
            worst_result = max(scorecard_data_list, key=lambda x: x['par_diff'])
        else:
            best_result = worst_result = None
        
        # Mostrar estadísticas
        print(format_subtitle(f"Estadísticas de {course.name}"))
        print(f"Par del campo: {course.par_total}")
        print(f"Slope: {course.slope}")
        print(f"Course Rating: {course.course_rating}")
        print(f"Total de rondas: {total_rounds}")
        print(f"Media de golpes: {avg_strokes:.1f}")
        print(f"Media respecto al par: {avg_par_diff:+.1f}")
        print(f"Media de puntos stableford: {avg_points:.1f}")
        
        if best_result:
            print(format_subtitle("Mejor resultado"))
            print(f"Jugador: {best_result['player_name']}")
            print(f"Fecha: {best_result['date']}")
            print(f"Golpes: {best_result['total_strokes']}")
            print(f"Resultado: {best_result['result_str']}")
            
            print(format_subtitle("Peor resultado"))
            print(f"Jugador: {worst_result['player_name']}")
            print(f"Fecha: {worst_result['date']}")
            print(f"Golpes: {worst_result['total_strokes']}")
            print(f"Resultado: {worst_result['result_str']}")
        
        pause()
        self.show_statistics()
    
    def _show_best_results(self):
        """
        Muestra los mejores resultados.
        """
        clear_screen()
        print(format_title("MEJORES RESULTADOS"))
        
        # Obtener todas las tarjetas
        scorecards = self.controller.get_scorecards()
        
        if not scorecards:
            print(format_info("No hay tarjetas registradas."))
            pause()
            self.show_statistics()
            return
        
        # Preparar datos para estadísticas
        scorecard_data_list = []
        for sc in scorecards:
            player = self.player_controller.get_player(sc.player_id)
            course = self.course_controller.get_course(sc.course_id)
            
            if not player or not course:
                continue
            
            scorecard_data = ScorecardUtils.prepare_scorecard_data(
                sc, self.player_controller, self.course_controller, player, course
            )
            
            # Añadir información para estadísticas
            scorecard_data['par_diff'] = scorecard_data['total_strokes'] - course.par_total
            scorecard_data['scorecard'] = sc
            
            scorecard_data_list.append(scorecard_data)
        
        if not scorecard_data_list:
            print(format_info("No hay datos suficientes para mostrar estadísticas."))
            pause()
            self.show_statistics()
            return
        
        # Ordenar por resultado respecto al par (mejor a peor)
        best_results = sorted(scorecard_data_list, key=lambda x: x['par_diff'])[:10]
        
        # Ordenar por puntos stableford (mejor a peor)
        best_points = sorted(scorecard_data_list, key=lambda x: x['total_points'], reverse=True)[:10]
        
        # Mostrar mejores resultados respecto al par
        print(format_subtitle("Mejores resultados respecto al par"))
        
        headers = ["Jugador", "Campo", "Fecha", "Golpes", "Resultado"]
        data = []
        
        for result in best_results:
            data.append([
                result['player_name'],
                result['course_name'],
                result['date'],
                result['total_strokes'],
                result['result_str']
            ])
        
        print(format_table(data, headers))
        
        # Mostrar mejores resultados stableford
        print(format_subtitle("Mejores resultados stableford"))
        
        headers = ["Fecha", "Campo", "Golpes", "Puntos"]
        data = []
        
        for result in best_points:
            data.append([
                result['date'],
                result['course_name'],
                result['total_strokes'],
                result['total_points']
            ])
        
        print(format_table(data, headers))
        
        pause()
        self.show_statistics()
    
    def _show_handicap_evolution(self):
        """
        Muestra la evolución del hándicap de un jugador.
        """
        clear_screen()
        print(format_title("EVOLUCIÓN DE HÁNDICAP"))
        
        # Seleccionar jugador
        print(format_subtitle("Seleccionar jugador"))
        player_id = self.player_view.select_player()
        if player_id is None:
            self.show_statistics()
            return
        
        player = self.player_controller.get_player(player_id)
        if not player:
            print(format_info("No se pudo obtener la información del jugador."))
            pause()
            self.show_statistics()
            return
        
        # Obtener tarjetas del jugador
        scorecards = self.controller.get_scorecards()
        player_scorecards = [sc for sc in scorecards if sc.player_id == player_id]
        
        if not player_scorecards:
            print(format_info(f"No hay tarjetas registradas para {player.first_name} {player.surname}."))
            pause()
            self.show_statistics()
            return
        
        # Ordenar tarjetas por fecha
        player_scorecards.sort(key=lambda x: x.date)
        
        # Preparar datos para la tabla
        headers = ["Fecha", "Campo", "Golpes", "Puntos", "Hándicap"]
        data = []
        
        for sc in player_scorecards:
            course = self.course_controller.get_course(sc.course_id)
            if not course:
                continue
            
            scorecard_data = ScorecardUtils.prepare_scorecard_data(
                sc, self.player_controller, self.course_controller, player, course
            )
            
            # Calcular hándicap de juego
            handicap_coefficient = sc.handicap_coefficient
            base_handicap = round((handicap_coefficient * 113) / course.slope, 1)
            
            data.append([
                scorecard_data['date'],
                scorecard_data['course_name'],
                scorecard_data['total_strokes'],
                scorecard_data['total_points'],
                base_handicap
            ])
        
        # Mostrar tabla
        print(format_subtitle(f"Evolución de hándicap de {player.first_name} {player.surname}"))
        print(format_table(data, headers))
        
        # Mostrar hándicap actual
        print(f"Hándicap actual: {player.handicap}")
        
        pause()
        self.show_statistics()
