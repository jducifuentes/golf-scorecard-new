"""
Vista para la visualización y gestión de listas de tarjetas.
"""
from colorama import Fore, Style
from src.views.base_view import BaseView
from src.views.utils import format_title, format_info, format_table, clear_screen, pause, format_error
from src.utils.formatters import format_menu_option
from src.utils.helpers_simple import get_number_input
from src.views.scorecard.scorecard_utils import ScorecardUtils


class ScorecardListView(BaseView):
    """
    Vista para mostrar y gestionar listas de tarjetas de puntuación.
    """
    
    def __init__(self, scorecard_controller, player_controller, course_controller):
        """
        Inicializa la vista de listas de tarjetas.
        
        Args:
            scorecard_controller: Controlador de tarjetas
            player_controller: Controlador de jugadores
            course_controller: Controlador de campos
        """
        super().__init__()
        self.scorecard_controller = scorecard_controller
        self.player_controller = player_controller
        self.course_controller = course_controller
    
    def display_scorecards_list(self, scorecards):
        """
        Muestra una lista de tarjetas y permite seleccionar una para ver detalles.
        
        Args:
            scorecards (list): Lista de tarjetas a mostrar
            
        Returns:
            Scorecard: La tarjeta seleccionada o None si se cancela
        """
        while True:
            clear_screen()
            print(format_title("LISTA DE TARJETAS"))
            
            if not scorecards:
                print(format_info("\nNo hay tarjetas disponibles."))
                pause()
                return None
            
            # Preparar datos para la tabla
            table_data = []
            for i, sc in enumerate(scorecards):
                # Obtener nombres de jugador y campo
                player_name = "No disponible"
                if hasattr(sc, 'player_id') and sc.player_id:
                    if hasattr(sc, 'player_name') and sc.player_name:
                        player_name = sc.player_name
                    else:
                        player = self.player_controller.get_player(sc.player_id)
                        if player:
                            player_name = f"{player.first_name} {player.surname}"
                        else:
                            player_name = f"ID: {sc.player_id}"
                
                course_name = "No disponible"
                if hasattr(sc, 'course_id') and sc.course_id:
                    if hasattr(sc, 'course_name') and sc.course_name:
                        course_name = sc.course_name
                    else:
                        course = self.course_controller.get_course(sc.course_id)
                        if course:
                            course_name = course.name
                        else:
                            course_name = f"ID: {sc.course_id}"
                
                # Formatear fecha de YYYY-MM-DD a DD/MM/YYYY para mostrar
                display_date = "No disponible"
                if hasattr(sc, 'date') and sc.date:
                    try:
                        date_parts = sc.date.split('-') if sc.date else ['', '', '']
                        display_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}" if len(date_parts) == 3 else sc.date
                    except Exception:
                        display_date = sc.date
                
                # Calcular totales con manejo de errores
                try:
                    total_strokes = sc.total_strokes() if hasattr(sc, 'total_strokes') else 0
                except Exception:
                    total_strokes = 0
                
                try:
                    total_points = sc.total_points() if hasattr(sc, 'total_points') else 0
                except Exception:
                    total_points = 0
                
                # Añadir fila a la tabla
                table_data.append([
                    i + 1,
                    player_name,
                    course_name,
                    display_date,
                    total_strokes,
                    total_points
                ])
            
            # Mostrar tabla
            headers = ["#",  "Jugador", "Campo", "Fecha", "Golpes", "Puntos"]
            print("\n" + format_table(headers, table_data))
            
            # Opciones
            print("\nOpciones:")
            print("  1-{}: Seleccionar tarjeta".format(len(scorecards)))
            print("  0: Volver")
            
            # Solicitar opción
            option = input("\nSeleccione una opción: ")
            
            if option == "0":
                return None
            
            try:
                index = int(option) - 1
                if 0 <= index < len(scorecards):
                    return scorecards[index]
                else:
                    print(format_error("Opción inválida. Debe ser un número entre 1 y {}".format(len(scorecards))))
                    pause()
            except ValueError:
                print(format_error("Opción inválida. Debe ingresar un número."))
                pause()
    
    def show_all_scorecards(self):
        """
        Muestra todas las tarjetas de puntuación.
        """
        scorecards = self.scorecard_controller.get_scorecards()
        
        if not scorecards:
            clear_screen()
            print(format_title("TARJETAS DE PUNTUACIÓN"))
            print(format_info("\nNo hay tarjetas registradas."))
            pause()
            return
        
        selected_scorecard = self.display_scorecards_list(scorecards)
        if selected_scorecard:
            return selected_scorecard
    
    def search_scorecards(self):
        """
        Busca tarjetas según criterios.
        
        Returns:
            Scorecard: La tarjeta seleccionada o None si se cancela
        """
        clear_screen()
        print(format_title("BUSCAR TARJETAS"))
        
        # Verificar si hay jugadores y campos
        players = self.player_controller.get_players()
        courses = self.course_controller.get_courses()
        
        if not players:
            print(format_info("No hay jugadores registrados. Debe crear al menos un jugador antes de buscar tarjetas."))
            pause()
            return None
        
        if not courses:
            print(format_info("No hay campos registrados. Debe crear al menos un campo antes de buscar tarjetas."))
            pause()
            return None
        
        # Mostrar opciones de búsqueda
        print(f"\n{Fore.YELLOW}Opciones de búsqueda:{Style.RESET_ALL}")
        print(format_menu_option("1", "Por jugador"))
        print(format_menu_option("2", "Por campo"))
        print(format_menu_option("3", "Por fecha"))
        print(format_menu_option("0", "Volver"))
        
        option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=3, allow_float=False)
        
        if option == 0:
            return None
        elif option == 1:
            # Buscar por jugador
            clear_screen()
            print(format_title("BUSCAR POR JUGADOR"))
            
            # Mostrar lista de jugadores
            print("\nJugadores disponibles:")
            for i, player in enumerate(players):
                print(f"  {i+1}. {player.first_name} {player.surname}")
            
            player_option = get_number_input("\nSeleccione un jugador (0 para cancelar)", default=0, min_value=0, max_value=len(players), allow_float=False)
            
            if player_option == 0:
                return self.search_scorecards()
            
            try:
                player_index = player_option - 1
                if 0 <= player_index < len(players):
                    player_id = players[player_index].id
                    scorecards = self.scorecard_controller.search_scorecards({'player_id': player_id})
                    
                    if not scorecards:
                        print(format_info("No se encontraron tarjetas para este jugador."))
                        pause()
                        return self.search_scorecards()
                    
                    return self.display_scorecards_list(scorecards)
                else:
                    print(format_error("Opción inválida."))
                    pause()
                    return self.search_scorecards()
            except ValueError:
                print(format_error("Opción inválida. Debe ingresar un número."))
                pause()
                return self.search_scorecards()
        
        elif option == 2:
            # Buscar por campo
            clear_screen()
            print(format_title("BUSCAR POR CAMPO"))
            
            # Mostrar lista de campos
            print("\nCampos disponibles:")
            for i, course in enumerate(courses):
                print(f"  {i+1}. {course.name} ({course.location})")
            
            course_option = get_number_input("\nSeleccione un campo (0 para cancelar)", default=0, min_value=0, max_value=len(courses), allow_float=False)
            
            if course_option == 0:
                return self.search_scorecards()
            
            try:
                course_index = course_option - 1
                if 0 <= course_index < len(courses):
                    course_id = courses[course_index].id
                    scorecards = self.scorecard_controller.search_scorecards({'course_id': course_id})
                    
                    if not scorecards:
                        print(format_info("No se encontraron tarjetas para este campo."))
                        pause()
                        return self.search_scorecards()
                    
                    return self.display_scorecards_list(scorecards)
                else:
                    print(format_error("Opción inválida."))
                    pause()
                    return self.search_scorecards()
            except ValueError:
                print(format_error("Opción inválida. Debe ingresar un número."))
                pause()
                return self.search_scorecards()
        
        elif option == 3:
            # Buscar por fecha
            clear_screen()
            print(format_title("BUSCAR POR FECHA"))
            
            date = input("\nIngrese la fecha (YYYY-MM-DD) o parte de ella: ")
            
            if not date:
                return self.search_scorecards()
            
            scorecards = self.scorecard_controller.search_scorecards({'date': date})
            
            if not scorecards:
                print(format_info("No se encontraron tarjetas para esta fecha."))
                pause()
                return self.search_scorecards()
            
            return self.display_scorecards_list(scorecards)
        
        else:
            print(format_error("Opción inválida."))
            pause()
            return self.search_scorecards()
