"""
Vista para la creación de tarjetas de puntuación.
"""
from colorama import Fore, Style
from datetime import datetime
from src.views.base_view import BaseView
from src.views.utils import format_title, format_info, clear_screen, pause
from src.views.player_view import PlayerView
from src.views.course_view import CourseView


class ScorecardCreateView(BaseView):
    """
    Vista para crear nuevas tarjetas de puntuación.
    """
    
    def __init__(self, scorecard_controller, player_controller, course_controller):
        """
        Inicializa la vista de creación de tarjetas.
        
        Args:
            scorecard_controller: Controlador de tarjetas
            player_controller: Controlador de jugadores
            course_controller: Controlador de campos
        """
        super().__init__()
        self.scorecard_controller = scorecard_controller
        self.player_controller = player_controller
        self.course_controller = course_controller
    
    def create_scorecard(self):
        """
        Crea una nueva tarjeta de puntuación.
        
        Returns:
            bool: True si se creó correctamente, False en caso contrario
        """
        clear_screen()
        print(format_title("CREAR NUEVA TARJETA"))
        
        # Verificar si hay jugadores y campos
        players = self.player_controller.get_players()
        courses = self.course_controller.get_courses()
        
        if not players:
            print(f"{Fore.YELLOW}No hay jugadores registrados. Debe crear al menos un jugador antes de crear una tarjeta.{Style.RESET_ALL}")
            
            # Preguntar si desea crear un jugador
            if input("¿Desea crear un jugador ahora? (s/n): ").lower() == 's':
                player_view = PlayerView(self.scorecard_controller.db)
                player_view.add_player()
                # Recargar la lista de jugadores
                players = self.player_controller.get_players()
                if not players:
                    pause()
                    return False
            else:
                pause()
                return False
        
        if not courses:
            print(f"{Fore.YELLOW}No hay campos registrados. Debe crear al menos un campo antes de crear una tarjeta.{Style.RESET_ALL}")
            
            # Preguntar si desea crear un campo
            if input("¿Desea crear un campo ahora? (s/n): ").lower() == 's':
                course_view = CourseView(self.scorecard_controller.db)
                course_view.add_course()
                # Recargar la lista de campos
                courses = self.course_controller.get_courses()
                if not courses:
                    pause()
                    return False
            else:
                pause()
                return False
        
        # Seleccionar jugador
        print(f"\n{Fore.CYAN}Seleccione un jugador:{Style.RESET_ALL}")
        for i, player in enumerate(players):
            print(f"  {i+1}. {player.first_name} {player.surname} (Hándicap: {player.handicap})")
        print(f"  0. Añadir nuevo jugador")
        
        player_option = input("\nNúmero de jugador (0 para añadir nuevo): ")
        
        if player_option == "0":
            # Crear nuevo jugador
            player_view = PlayerView(self.scorecard_controller.db)
            player_view.add_player()
            # Recargar la lista de jugadores y volver a mostrar la selección
            return self.create_scorecard()
        
        try:
            player_index = int(player_option) - 1
            if 0 <= player_index < len(players):
                player = players[player_index]
            else:
                print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")
                pause()
                return False
        except ValueError:
            print(f"{Fore.RED}Opción inválida. Debe ingresar un número.{Style.RESET_ALL}")
            pause()
            return False
        
        # Seleccionar campo
        clear_screen()
        print(format_title("CREAR NUEVA TARJETA"))
        print(f"Jugador seleccionado: {player.first_name} {player.surname}")
        
        print(f"\n{Fore.CYAN}Seleccione un campo:{Style.RESET_ALL}")
        for i, course in enumerate(courses):
            print(f"  {i+1}. {course.name} ({course.location})")
        print(f"  0. Añadir nuevo campo")
        
        course_option = input("\nNúmero de campo (0 para añadir nuevo): ")
        
        if course_option == "0":
            # Crear nuevo campo
            course_view = CourseView(self.scorecard_controller.db)
            course_view.add_course()
            # Recargar la lista de campos y volver a la selección de campo
            # Mantenemos el jugador seleccionado
            courses = self.course_controller.get_courses()
            if not courses:
                print(f"{Fore.RED}No se pudo crear un campo. Operación cancelada.{Style.RESET_ALL}")
                pause()
                return False
                
            # Volver a mostrar la selección de campo
            clear_screen()
            print(format_title("CREAR NUEVA TARJETA"))
            print(f"Jugador seleccionado: {player.first_name} {player.surname}")
            
            print(f"\n{Fore.CYAN}Seleccione un campo:{Style.RESET_ALL}")
            for i, course in enumerate(courses):
                print(f"  {i+1}. {course.name} ({course.location})")
            print(f"  0. Añadir nuevo campo")
            
            course_option = input("\nNúmero de campo (0 para añadir nuevo): ")
            
            if course_option == "0":
                print(f"{Fore.RED}Operación cancelada.{Style.RESET_ALL}")
                pause()
                return False
        
        try:
            course_index = int(course_option) - 1
            if 0 <= course_index < len(courses):
                course = courses[course_index]
            else:
                print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")
                pause()
                return False
        except ValueError:
            print(f"{Fore.RED}Opción inválida. Debe ingresar un número.{Style.RESET_ALL}")
            pause()
            return False
        
        # Ingresar fecha
        clear_screen()
        print(format_title("CREAR NUEVA TARJETA"))
        print(f"Jugador: {player.first_name} {player.surname}")
        print(f"Campo: {course.name}")
        
        today = datetime.now().strftime("%Y-%m-%d")
        date_input = input(f"\nFecha (YYYY-MM-DD, Enter para usar hoy [{today}]): ")
        date = date_input if date_input else today
        
        # Ingresar hándicap de juego
        clear_screen()
        print(format_title("CREAR NUEVA TARJETA"))
        print(f"Jugador: {player.first_name} {player.surname}")
        print(f"Campo: {course.name}")
        print(f"Fecha: {date}")
        
        # Calcular hándicap de juego sugerido
        suggested_handicap = round(player.handicap * (course.slope/113), 1)
        
        print(f"\nHándicap del jugador: {player.handicap}")
        print(f"Slope del campo: {course.slope}")
        print(f"Hándicap de juego sugerido: {suggested_handicap}")
        
        handicap_input = input(f"Hándicap de juego (Enter para usar sugerido [{suggested_handicap}]): ")
        
        try:
            playing_handicap = float(handicap_input) if handicap_input else suggested_handicap
        except ValueError:
            print(f"{Fore.RED}Valor inválido. Se usará el hándicap sugerido.{Style.RESET_ALL}")
            playing_handicap = suggested_handicap
            pause()
        
        # Ingresar coeficiente de hándicap
        handicap_coef_input = input("Coeficiente de hándicap (%) [100]: ")
        
        try:
            handicap_coefficient = int(handicap_coef_input) if handicap_coef_input else 100
        except ValueError:
            print(f"{Fore.RED}Valor inválido. Se usará 100%.{Style.RESET_ALL}")
            handicap_coefficient = 100
            pause()
        
        # Ingresar golpes por hoyo
        clear_screen()
        print(format_title("INGRESAR GOLPES"))
        
        print(f"Jugador: {player.first_name} {player.surname}")
        print(f"Campo: {course.name}")
        print(f"Fecha: {date}")
        print(f"Hándicap de juego: {playing_handicap}")
        
        print(f"\n{Fore.CYAN}Ingrese los golpes para cada hoyo:{Style.RESET_ALL}")
        print("(Deje en blanco para terminar la entrada de datos)")
        
        strokes = []
        
        for i, par in enumerate(course.hole_pars):
            hole_num = i + 1
            
            while True:
                stroke_input = input(f"Hoyo {hole_num} (Par {par}): ")
                
                if stroke_input == "":
                    break
                
                try:
                    stroke = int(stroke_input)
                    if stroke <= 0:
                        print(f"{Fore.RED}El número de golpes debe ser positivo.{Style.RESET_ALL}")
                        continue
                    
                    strokes.append(stroke)
                    break
                except ValueError:
                    print(f"{Fore.RED}Valor inválido. Debe ingresar un número entero.{Style.RESET_ALL}")
            
            if stroke_input == "":
                break
        
        # Confirmar creación
        clear_screen()
        print(format_title("CONFIRMAR TARJETA"))
        
        print(f"Jugador: {player.first_name} {player.surname}")
        print(f"Campo: {course.name}")
        print(f"Fecha: {date}")
        print(f"Hándicap de juego: {playing_handicap}")
        print(f"Coeficiente de hándicap: {handicap_coefficient}%")
        
        if strokes:
            print(f"\nGolpes por hoyo:")
            for i, stroke in enumerate(strokes):
                hole_num = i + 1
                par = course.hole_pars[i] if i < len(course.hole_pars) else "?"
                print(f"  Hoyo {hole_num} (Par {par}): {stroke}")
            
            print(f"\nTotal golpes: {sum(strokes)}")
        else:
            print(f"\nNo se ingresaron golpes.")
        
        confirm = input("\n¿Desea crear esta tarjeta? (s/n): ")
        
        if confirm.lower() == 's':
            success, result = self.scorecard_controller.create_scorecard(
                player.id,
                course.id,
                date,
                strokes,
                playing_handicap,
                handicap_coefficient
            )
            
            if success:
                print(f"{Fore.GREEN}Tarjeta creada correctamente con ID #{result}.{Style.RESET_ALL}")
                pause()
                return True
            else:
                print(f"{Fore.RED}Error al crear la tarjeta: {result}{Style.RESET_ALL}")
                pause()
                return False
        else:
            print("Operación cancelada.")
            pause()
            return False
