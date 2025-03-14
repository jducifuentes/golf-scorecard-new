"""
Vista para mostrar tarjetas de puntuación.
"""
from colorama import Fore, Style
from src.controllers.scorecard_controller import ScorecardController
from src.controllers.player_controller import PlayerController
from src.controllers.course_controller import CourseController
from src.utils.formatters import (
    format_title, format_subtitle, format_table, format_info, 
    format_error, format_scorecard_header, format_scorecard_table,
    format_menu_option, format_warning
)
from src.utils.helpers_simple import (
    clear_screen, pause, get_number_input, calculate_handicap_strokes
)
from src.views.scorecard.scorecard_utils import ScorecardUtils

class ScorecardDisplayView:
    """
    Vista para mostrar tarjetas de puntuación.
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
    
    def show_scorecards(self):
        """
        Muestra la lista de tarjetas.
        Muestra solo las 10 tarjetas más recientes ordenadas de más antigua a más nueva.
        """
        clear_screen()
        print(format_title("LISTA DE TARJETAS"))
        scorecards = self.controller.get_scorecards()
        if not scorecards:
            print(format_info("No hay tarjetas registradas."))
            pause()
            return
        
        # Ordenar tarjetas por fecha (más recientes primero)
        scorecards.sort(key=lambda x: x.date, reverse=True)
        
        # Tomar solo las 10 más recientes
        recent_scorecards = scorecards[:10]
        
        # Ordenar de más antigua a más nueva para mostrar
        recent_scorecards.sort(key=lambda x: x.date)
        
        # Mostrar tabla de tarjetas
        headers = ["ID", "Fecha", "Jugador", "Campo", "Ubicación", "Golpes", "Resultado", "Puntos"]
        data = []
        
        for sc in recent_scorecards:
            scorecard_data = ScorecardUtils.prepare_scorecard_data(
                sc, self.player_controller, self.course_controller
            )
            data.append([
                scorecard_data['id'],
                scorecard_data['date'],
                scorecard_data['player_name'],
                scorecard_data['course_name'],
                scorecard_data['course_location'],
                scorecard_data['total_strokes'],
                scorecard_data['result_str'],
                scorecard_data['total_points']
            ])
        
        # Mostrar la tabla
        print(format_table(data, headers))
        
        # Opciones
        print(f"{Fore.YELLOW}Opciones:{Style.RESET_ALL}")
        print(format_menu_option("1", "Ver detalles de tarjeta"))
        print(format_menu_option("2", "Modificar tarjeta"))
        print(format_menu_option("3", "Eliminar tarjeta"))
        print(format_menu_option("4", "Filtrar tarjetas"))
        print(format_menu_option("0", "Volver"))
        
        option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=4, allow_float=False)
        
        if option == 0:
            return
        elif option == 1:
            # Solicitar ID para ver detalles
            scorecard_id = get_number_input("ID de la tarjeta a ver", allow_float=False)
            if scorecard_id is None:
                return
            self.view_scorecard_details(scorecard_id)
            return
        elif option == 2:
            # Solicitar ID para modificar
            scorecard_id = get_number_input("ID de la tarjeta a modificar", allow_float=False)
            if scorecard_id is None:
                return
            # Usar la vista de edición para modificar
            from src.views.scorecard.scorecard_edit import ScorecardEditView
            edit_view = ScorecardEditView(self.controller, self.player_controller, self.course_controller)
            edit_view.modify_scorecard(scorecard_id)
            return
        elif option == 3:
            # Solicitar ID para eliminar
            scorecard_id = get_number_input("ID de la tarjeta a eliminar", allow_float=False)
            if scorecard_id is None:
                return
            # Usar la vista de edición para eliminar
            from src.views.scorecard.scorecard_edit import ScorecardEditView
            edit_view = ScorecardEditView(self.controller, self.player_controller, self.course_controller)
            edit_view.delete_scorecard(scorecard_id)
            return
        elif option == 4:
            # Usar la vista de filtrado
            from src.views.scorecard.scorecard_filter import ScorecardFilterView
            filter_view = ScorecardFilterView(self.controller, self.player_controller, self.course_controller)
            # Iniciar filtrado desde cero (sin filtros previos)
            filter_view.filter_scorecards()
            # Después de filtrar, volver a mostrar la lista de tarjetas
            self.show_scorecards()
            return
    
    def view_scorecard_details(self, scorecard_id):
        """
        Muestra los detalles de una tarjeta.
        
        Args:
            scorecard_id (int): ID de la tarjeta a ver
        """
        clear_screen()
        print(format_title("DETALLES DE TARJETA"))
        
        # Obtener la tarjeta
        scorecard = self.controller.get_scorecard(scorecard_id)
        if not scorecard:
            print(format_error(f"No se encontró la tarjeta con ID {scorecard_id}"))
            pause()
            return
        
        # Mostrar detalles
        self.display_scorecard_details(scorecard)
        
        # Opciones
        print(f"{Fore.YELLOW}Opciones:{Style.RESET_ALL}")
        print(format_menu_option("1", "Modificar tarjeta"))
        print(format_menu_option("2", "Eliminar tarjeta"))
        print(format_menu_option("0", "Volver"))
        
        option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=2, allow_float=False)
        
        if option == 0:
            # En lugar de llamar a show_scorecards(), simplemente retornamos
            # para evitar la recursión infinita
            return
        elif option == 1:
            # Usar la vista de edición para modificar
            from src.views.scorecard.scorecard_edit import ScorecardEditView
            edit_view = ScorecardEditView(self.controller, self.player_controller, self.course_controller)
            edit_view.modify_scorecard(scorecard_id)
            return
        elif option == 2:
            # Usar la vista de edición para eliminar
            from src.views.scorecard.scorecard_edit import ScorecardEditView
            edit_view = ScorecardEditView(self.controller, self.player_controller, self.course_controller)
            edit_view.delete_scorecard(scorecard_id)
            return

    def display_scorecard_details(self, scorecard):
        """
        Muestra los detalles de una tarjeta.
        
        Args:
            scorecard (Scorecard): Tarjeta a mostrar
        """
        if not scorecard:
            print(format_error("No se encontró la tarjeta."))
            pause()
            return
        
        # Obtener información del jugador y campo
        player = self.player_controller.get_player(scorecard.player_id)
        
        # Mostrar cabecera
        clear_screen()
        print(format_title("DETALLES DE TARJETA"))
        print("-" * 60)
        
        # Información básica
        print(f"{Fore.CYAN}Jugador:{Style.RESET_ALL} {player.first_name} {player.surname}")
        print(f"{Fore.CYAN}Campo:{Style.RESET_ALL} {scorecard.course_name} - {scorecard.course_location}")
        print(f"{Fore.CYAN}Fecha:{Style.RESET_ALL} {scorecard.date}")
        print(f"{Fore.CYAN}Hándicap de juego:{Style.RESET_ALL} {scorecard.playing_handicap}")
        print(f"{Fore.CYAN}Coeficiente aplicado:{Style.RESET_ALL} {scorecard.handicap_coefficient}%")
        
        # Calcular golpes de hándicap por hoyo
        playing_handicap = scorecard.playing_handicap or 0  # Si es None, usar 0
        playing_coefficient = playing_handicap * (scorecard.handicap_coefficient / 100)
        
        # Usar los datos del curso almacenados en la tarjeta
        handicap_strokes = calculate_handicap_strokes(
            playing_coefficient, 
            scorecard.course_slope, 
            scorecard.course_rating, 
            scorecard.course_hole_handicaps
        )
        
        # Mostrar tabla de resultados
        print("\n" + format_subtitle("Resultados por hoyo"))
        
        # Preparar datos para la tabla
        headers = ["Hoyo", "Par", "Hcp", "Golpes Extra", "Golpes", "Resultado", "Puntos"]
        data = []
        
        total_strokes = 0
        total_points = 0
        
        # Verificar que tenemos datos de pars y handicaps
        if not scorecard.course_hole_pars or not scorecard.course_hole_handicaps:
            print(format_error("No se pudo obtener la información completa del campo."))
            pause()
            return
            
        # Verificar que tenemos datos de golpes y puntos
        if not scorecard.strokes or not scorecard.points:
            print(format_error("Esta tarjeta no tiene datos de golpes o puntos."))
            pause()
            return
        
        # Generar datos para la tabla
        for i in range(len(scorecard.strokes)):
            if i < len(scorecard.course_hole_pars) and i < len(scorecard.course_hole_handicaps):
                par = scorecard.course_hole_pars[i]
                handicap = scorecard.course_hole_handicaps[i]
                extra_strokes = handicap_strokes[i] if i < len(handicap_strokes) else 0
                strokes = scorecard.strokes[i]
                points = scorecard.points[i] if i < len(scorecard.points) else 0
                
                # Calcular resultado respecto al par
                result = strokes - par
                result_str = "E" if result == 0 else f"{'+' if result > 0 else ''}{result}"
                
                data.append([i+1, par, handicap, extra_strokes, strokes, result_str, points])
                
                total_strokes += strokes
                total_points += points
        
        # Mostrar tabla
        table = format_table(data, headers)
        print(table)
        
        # Mostrar totales
        print(f"\nTotal golpes: {total_strokes}")
        print(f"Total puntos: {total_points}")
        
        # Análisis de la ronda
        print("\n" + format_subtitle("Análisis de la ronda"))
        
        # Contar resultados por tipo
        eagles = 0
        birdies = 0
        pars = 0
        bogeys = 0
        double_bogeys_or_worse = 0
        
        for i in range(len(scorecard.strokes)):
            if i < len(scorecard.course_hole_pars):
                par = scorecard.course_hole_pars[i]
                strokes = scorecard.strokes[i]
                diff = strokes - par
                
                if diff <= -2:
                    eagles += 1
                elif diff == -1:
                    birdies += 1
                elif diff == 0:
                    pars += 1
                elif diff == 1:
                    bogeys += 1
                else:
                    double_bogeys_or_worse += 1
        
        print(f"Eagles (4 puntos): {eagles}")
        print(f"Birdies (3 puntos): {birdies}")
        print(f"Pares (2 puntos): {pars}")
        print(f"Bogeys (1 punto): {bogeys}")
        print(f"Doble bogeys o peor (0 puntos): {double_bogeys_or_worse}")
        
        pause()
