"""
Vista para filtrar tarjetas de puntuación.
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
    clear_screen, pause, get_input, get_number_input, 
    get_date_range_input
)
from src.views.scorecard.scorecard_utils import ScorecardUtils
from src.views.player_view import PlayerView
from src.views.course_view import CourseView

class ScorecardFilterView:
    """
    Vista para filtrar tarjetas de puntuación.
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
        self.current_filter_description = "Sin filtros"
        self.filtered_scorecards = None
        
    def filter_scorecards(self, scorecards=None, previous_filter_description=None):
        """
        Filtra tarjetas según criterios.
        
        Args:
            scorecards (list, optional): Lista de tarjetas previamente filtradas
            previous_filter_description (str, optional): Descripción del filtro previo
        """
        clear_screen()
        
        # Si tenemos un filtro previo, mostrarlo
        if previous_filter_description:
            self.current_filter_description = previous_filter_description
            print(format_title("FILTRAR TARJETAS"))
            print(format_subtitle(f"Filtro actual: {self.current_filter_description}"))
        else:
            print(format_title("FILTRAR TARJETAS"))
            
        # Si no se proporcionan tarjetas, obtener todas
        if scorecards is None:
            scorecards = self.controller.get_scorecards()
            self.current_filter_description = "Sin filtros"
        else:
            self.filtered_scorecards = scorecards
        
        print(format_menu_option("1", "Filtrar por jugador"))
        print(format_menu_option("2", "Filtrar por campo"))
        print(format_menu_option("3", "Filtrar por fecha"))
        print(format_menu_option("4", "Filtrar por resultado"))
        print(format_menu_option("0", "Volver"))
        
        option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=4, allow_float=False)
        
        if option == 0:
            # Volver a la vista de tarjetas
            from src.views.scorecard.scorecard_display import ScorecardDisplayView
            display_view = ScorecardDisplayView(self.controller, self.player_controller, self.course_controller)
            display_view.show_scorecards()
            return
        
        # Obtener todas las tarjetas
        if scorecards is None:
            scorecards = self.controller.get_scorecards()
        
        if not scorecards:
            print(format_info("No hay tarjetas registradas."))
            pause()
            return
        
        # Aplicar filtro según la opción seleccionada
        filtered_scorecards = []
        
        if option == 1:
            # Filtrar por jugador
            print(format_subtitle("Seleccionar jugador"))
            
            # Crear una vista temporal de jugadores para seleccionar
            from src.views.player_view import PlayerView
            player_view = PlayerView(self.player_controller)
            player_id = player_view.select_player()
            
            if not player_id:
                return
            
            # Obtener jugador
            player = self.player_controller.get_player(player_id)
            if not player:
                print(format_info("No se pudo obtener la información del jugador."))
                pause()
                return
            
            filtered_scorecards = [sc for sc in scorecards if sc.player_id == player_id]
            filter_description = f"Jugador: {player.first_name} {player.surname}"
            
        elif option == 2:
            # Filtrar por campo
            print(format_subtitle("Seleccionar campo"))
            
            # Crear una vista temporal de campos para seleccionar
            from src.views.course_view import CourseView
            course_view = CourseView(self.course_controller)
            course_id = course_view.select_course()
            
            if not course_id:
                return
            
            # Obtener campo
            course = self.course_controller.get_course(course_id)
            if not course:
                print(format_info("No se pudo obtener la información del campo."))
                pause()
                return
            
            filtered_scorecards = [sc for sc in scorecards if sc.course_id == course_id]
            filter_description = f"Campo: {course.name}"
            
        elif option == 3:
            # Filtrar por fecha
            print(format_subtitle("Seleccionar rango de fechas"))
            date_range = get_date_range_input("Rango de fechas (DD/MM/YYYY - DD/MM/YYYY)")
            if not date_range:
                return
            
            start_date, end_date = date_range
            
            # Si ambas fechas son None, mostrar todas las tarjetas
            if start_date is None and end_date is None:
                filtered_scorecards = scorecards
                filter_description = "Todas las fechas"
            else:
                # Las fechas ya vienen en formato YYYY-MM-DD, no necesitan conversión
                filtered_scorecards = [sc for sc in scorecards if start_date <= sc.date <= end_date]
                
                # Convertir a formato DD/MM/YYYY para mostrar
                if start_date and end_date:
                    # Convertir de YYYY-MM-DD a DD/MM/YYYY para mostrar
                    start_parts = start_date.split('-')
                    end_parts = end_date.split('-')
                    
                    if len(start_parts) == 3 and len(end_parts) == 3:
                        start_display = f"{start_parts[2]}/{start_parts[1]}/{start_parts[0]}"
                        end_display = f"{end_parts[2]}/{end_parts[1]}/{end_parts[0]}"
                        filter_description = f"Fechas: {start_display} - {end_display}"
                    else:
                        filter_description = f"Fechas: {start_date} - {end_date}"
                else:
                    filter_description = f"Fechas: {start_date} - {end_date}"
            
        elif option == 4:
            # Filtrar por resultado
            print(format_subtitle("Seleccionar criterio de resultado"))
            print(format_menu_option("1", "Bajo par"))
            print(format_menu_option("2", "Par"))
            print(format_menu_option("3", "Sobre par"))
            print(format_menu_option("0", "Volver"))
            
            result_option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=3, allow_float=False)
            
            if result_option == 0:
                return
            
            # Preparar datos para filtrar
            scorecard_data_list = []
            for sc in scorecards:
                course = self.course_controller.get_course(sc.course_id)
                if not course:
                    continue
                
                scorecard_data = ScorecardUtils.prepare_scorecard_data(
                    sc, self.player_controller, self.course_controller, None, course
                )
                
                # Añadir información para filtrado
                scorecard_data['par_diff'] = scorecard_data['total_strokes'] - course.par_total
                scorecard_data['scorecard'] = sc
                
                scorecard_data_list.append(scorecard_data)
            
            # Aplicar filtro según resultado
            if result_option == 1:
                # Bajo par
                filtered_data = [data for data in scorecard_data_list if data['par_diff'] < 0]
                filter_description = "Resultado: Bajo par"
            elif result_option == 2:
                # Par
                filtered_data = [data for data in scorecard_data_list if data['par_diff'] == 0]
                filter_description = "Resultado: Par"
            elif result_option == 3:
                # Sobre par
                filtered_data = [data for data in scorecard_data_list if data['par_diff'] > 0]
                filter_description = "Resultado: Sobre par"
            
            # Extraer tarjetas filtradas
            filtered_scorecards = [data['scorecard'] for data in filtered_data]
        
        # Mostrar resultados
        self._show_filtered_scorecards(filtered_scorecards, filter_description)
    
    def _show_filtered_scorecards(self, scorecards, filter_description):
        """
        Muestra las tarjetas filtradas.
        
        Args:
            scorecards (list): Lista de tarjetas filtradas
            filter_description (str): Descripción del filtro aplicado
        """
        clear_screen()
        print(format_title("TARJETAS FILTRADAS"))
        
        # Mostrar el filtro actual
        if self.current_filter_description != "Sin filtros" and self.current_filter_description != filter_description:
            print(format_subtitle(f"Filtro anterior: {self.current_filter_description}"))
            print(format_subtitle(f"Filtro aplicado: {filter_description}"))
            # Actualizar el filtro actual combinando el anterior y el nuevo
            combined_filter = f"{self.current_filter_description} + {filter_description}"
            self.current_filter_description = combined_filter
        else:
            print(format_subtitle(f"Filtro: {filter_description}"))
            self.current_filter_description = filter_description
        
        if not scorecards:
            print(format_info("No se encontraron tarjetas que cumplan con los criterios."))
            pause()
            self.filter_scorecards()
            return
        
        # Guardar las tarjetas filtradas para uso posterior
        self.filtered_scorecards = scorecards
        
        # Mostrar tabla de tarjetas
        headers = ["ID", "Fecha", "Jugador", "Campo", "Golpes", "Resultado", "Puntos"]
        data = []
        
        for sc in scorecards:
            scorecard_data = ScorecardUtils.prepare_scorecard_data(
                sc, self.player_controller, self.course_controller
            )
            data.append([
                scorecard_data['id'],
                scorecard_data['date'],
                scorecard_data['player_name'],
                scorecard_data['course_name'],
                scorecard_data['total_strokes'],
                scorecard_data['result_str'],
                scorecard_data['total_points']
            ])
        
        # Mostrar la tabla
        print(format_table(data, headers))
        
        # Opciones
        print(f"{Fore.YELLOW}Opciones:{Style.RESET_ALL}")
        print(format_menu_option("1", "Ver detalles de tarjeta"))
        print(format_menu_option("2", "Filtrar estos resultados"))
        print(format_menu_option("3", "Nuevo filtro desde cero"))
        print(format_menu_option("0", "Volver"))
        
        option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=3, allow_float=False)
        
        if option == 0:
            # Volver a la vista de tarjetas
            return
        elif option == 1:
            # Ver detalles de tarjeta
            scorecard_id = get_number_input("ID de la tarjeta a ver", allow_float=False)
            if scorecard_id is None:
                self._show_filtered_scorecards(scorecards, self.current_filter_description)
                return
                
            from src.views.scorecard.scorecard_display import ScorecardDisplayView
            display_view = ScorecardDisplayView(self.controller, self.player_controller, self.course_controller)
            display_view.view_scorecard_details(scorecard_id)
            # Volver a mostrar los resultados filtrados
            self._show_filtered_scorecards(scorecards, self.current_filter_description)
            return
        elif option == 2:
            # Filtrar estos resultados
            self.filter_scorecards(scorecards, self.current_filter_description)
            return
        elif option == 3:
            # Nuevo filtro desde cero
            self.current_filter_description = "Sin filtros"
            self.filtered_scorecards = None
            self.filter_scorecards()
            return
