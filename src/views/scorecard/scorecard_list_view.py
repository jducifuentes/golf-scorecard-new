"""
Vista para la visualización y gestión de listas de tarjetas.
"""
from colorama import Fore, Style
from src.views.base_view import BaseView
from src.views.utils import format_title, format_info, format_table, clear_screen, pause
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
                    sc.id,
                    player_name,
                    course_name,
                    display_date,
                    total_strokes,
                    total_points
                ])
            
            # Mostrar tabla
            headers = ["#", "ID", "Jugador", "Campo", "Fecha", "Golpes", "Puntos"]
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
                    print(f"{Fore.RED}Opción inválida. Debe ser un número entre 1 y {len(scorecards)}.{Style.RESET_ALL}")
                    pause()
            except ValueError:
                print(f"{Fore.RED}Opción inválida. Debe ingresar un número.{Style.RESET_ALL}")
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
            print(f"{Fore.YELLOW}No hay jugadores registrados. Debe crear al menos un jugador antes de buscar tarjetas.{Style.RESET_ALL}")
            pause()
            return None
        
        if not courses:
            print(f"{Fore.YELLOW}No hay campos registrados. Debe crear al menos un campo antes de buscar tarjetas.{Style.RESET_ALL}")
            pause()
            return None
        
        # Mostrar opciones de búsqueda
        print("\nOpciones de búsqueda:")
        print("  1. Por jugador")
        print("  2. Por campo")
        print("  3. Por fecha")
        print("  4. Volver")
        
        option = input("\nSeleccione una opción: ")
        
        if option == "1":
            # Buscar por jugador
            clear_screen()
            print(format_title("BUSCAR POR JUGADOR"))
            
            # Mostrar lista de jugadores
            print("\nJugadores disponibles:")
            for i, player in enumerate(players):
                print(f"  {i+1}. {player.first_name} {player.surname}")
            
            player_option = input("\nSeleccione un jugador (0 para cancelar): ")
            
            if player_option == "0":
                return self.search_scorecards()
            
            try:
                player_index = int(player_option) - 1
                if 0 <= player_index < len(players):
                    player_id = players[player_index].id
                    scorecards = self.scorecard_controller.search_scorecards({'player_id': player_id})
                    
                    if not scorecards:
                        print(f"{Fore.YELLOW}No se encontraron tarjetas para este jugador.{Style.RESET_ALL}")
                        pause()
                        return self.search_scorecards()
                    
                    return self.display_scorecards_list(scorecards)
                else:
                    print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")
                    pause()
                    return self.search_scorecards()
            except ValueError:
                print(f"{Fore.RED}Opción inválida. Debe ingresar un número.{Style.RESET_ALL}")
                pause()
                return self.search_scorecards()
        
        elif option == "2":
            # Buscar por campo
            clear_screen()
            print(format_title("BUSCAR POR CAMPO"))
            
            # Mostrar lista de campos
            print("\nCampos disponibles:")
            for i, course in enumerate(courses):
                print(f"  {i+1}. {course.name} ({course.location})")
            
            course_option = input("\nSeleccione un campo (0 para cancelar): ")
            
            if course_option == "0":
                return self.search_scorecards()
            
            try:
                course_index = int(course_option) - 1
                if 0 <= course_index < len(courses):
                    course_id = courses[course_index].id
                    scorecards = self.scorecard_controller.search_scorecards({'course_id': course_id})
                    
                    if not scorecards:
                        print(f"{Fore.YELLOW}No se encontraron tarjetas para este campo.{Style.RESET_ALL}")
                        pause()
                        return self.search_scorecards()
                    
                    return self.display_scorecards_list(scorecards)
                else:
                    print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")
                    pause()
                    return self.search_scorecards()
            except ValueError:
                print(f"{Fore.RED}Opción inválida. Debe ingresar un número.{Style.RESET_ALL}")
                pause()
                return self.search_scorecards()
        
        elif option == "3":
            # Buscar por fecha
            clear_screen()
            print(format_title("BUSCAR POR FECHA"))
            
            date = input("\nIngrese la fecha (YYYY-MM-DD) o parte de ella: ")
            
            if not date:
                return self.search_scorecards()
            
            scorecards = self.scorecard_controller.search_scorecards({'date': date})
            
            if not scorecards:
                print(f"{Fore.YELLOW}No se encontraron tarjetas para esta fecha.{Style.RESET_ALL}")
                pause()
                return self.search_scorecards()
            
            return self.display_scorecards_list(scorecards)
        
        elif option == "4":
            return None
        
        else:
            print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")
            pause()
            return self.search_scorecards()
