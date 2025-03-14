"""
Vista para el menú principal de la aplicación (versión simplificada).
"""
import sys
from colorama import Fore, Style, init
from tabulate import tabulate

from src.views.player_view import PlayerView
from src.views.course_view import CourseView
from src.views.scorecard_view import ScorecardView
from src.utils.formatters import format_title, format_menu_option, format_info
from src.utils.helpers_simple import clear_screen, get_input, get_number_input

# Inicializar colorama
init(autoreset=True)

class MenuViewSimple:
    """
    Vista para el menú principal de la aplicación (versión simplificada).
    """
    
    def __init__(self):
        """Inicializa la vista del menú"""
        self.player_view = PlayerView()
        self.course_view = CourseView()
        self.scorecard_view = ScorecardView()
        self.running = True
    
    def display_header(self):
        """Muestra la cabecera de la aplicación"""
        clear_screen()
        
        # Título centrado
        title = "GOLF SCORECARD MANAGER"
        subtitle = "Gestión de tarjetas de puntuación de golf"
        width = 70
        
        print("\n" + "=" * width)
        print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(width)}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{subtitle.center(width)}{Style.RESET_ALL}")
        print("=" * width + "\n")
    
    def display_menu(self):
        """Muestra el menú principal"""
        self.display_header()
        
        width = 70
        
        # Título del menú
        print(f"{'-' * width}")
        print(f"{Fore.BLUE}{Style.BRIGHT}{'MENU PRINCIPAL'.center(width)}{Style.RESET_ALL}")
        print(f"{'-' * width}")
        
        # Crear tablas para el menú usando tabulate
        # Tabla de jugadores y campos
        jugadores_campos = [
            [f"{Fore.YELLOW}{Style.BRIGHT}JUGADORES{Style.RESET_ALL}", f"{Fore.YELLOW}{Style.BRIGHT}CAMPOS{Style.RESET_ALL}"],
            ["-" * 33, "-" * 33],
            [format_menu_option('1', 'Jugadores'), format_menu_option('3', 'Campos')],
            [format_menu_option('2', 'Añadir jugador'), format_menu_option('4', 'Añadir campo')],
            ["", ""]
        ]
        
        # Tabla de tarjetas y sistema
        tarjetas_sistema = [
            [f"{Fore.YELLOW}{Style.BRIGHT}TARJETAS{Style.RESET_ALL}", f"{Fore.YELLOW}{Style.BRIGHT}SISTEMA{Style.RESET_ALL}"],
            ["-" * 33, "-" * 33],
            [format_menu_option('5', 'Tarjetas'), format_menu_option('q', 'Salir')],
            [format_menu_option('6', 'Añadir tarjeta'), ""],
            [format_menu_option('7', 'Filtrar tarjetas'), ""]
        ]
        
        # Mostrar tablas sin bordes y con alineación perfecta
        print(tabulate(jugadores_campos, tablefmt="plain", colalign=("left", "left")))
        print(f"{'-' * width}")
        print(tabulate(tarjetas_sistema, tablefmt="plain", colalign=("left", "left")))
        print(f"{'-' * width}\n")
    
    def handle_option(self, option):
        """
        Maneja la opción seleccionada por el usuario.
        
        Args:
            option (int or str): Opción seleccionada
        """
        # Opciones de jugadores
        if option == 1:
            self.player_view.show_players()
        elif option == 2:
            self.player_view.add_player()
        
        # Opciones de campos
        elif option == 3:
            self.course_view.show_courses()
        elif option == 4:
            self.course_view.add_course()
        
        # Opciones de tarjetas
        elif option == 5:
            self.scorecard_view.show_scorecards()
        elif option == 6:
            self.scorecard_view.add_scorecard()
        elif option == 7:
            self.scorecard_view.filter_scorecards()
        
        # Opciones de sistema
        elif option == 'q' :
            self.exit_application()
        
        else:
            print(format_info("Opción no válida. Por favor, intente nuevamente."))
    
    def exit_application(self):
        """Sale de la aplicación"""
        self.display_header()
        
        width = 70
        print("\n" + "=" * width)
        print(f"{Fore.GREEN}{Style.BRIGHT}{'¡Gracias por usar Golf Scorecard Manager!'.center(width)}{Style.RESET_ALL}")
        print("=" * width + "\n")
        
        self.running = False
    
    def run(self):
        """Ejecuta el bucle principal del menú"""
        try:
            while self.running:
                try:
                    self.display_menu()
                    
                    # Solicitar opción al usuario
                    print(f"{Fore.CYAN}> Seleccione una opción: {Style.RESET_ALL}", end="")
                    option = input().strip().lower()
                    
                    if not option:
                        continue
                    
                    # Convertir a número si es posible
                    if option.isdigit():
                        option = int(option)
                        if 1 <= option <= 7:
                            self.handle_option(option)
                        elif option == 0:
                            self.handle_option('q')
                        else:
                            print(format_info("Opción no válida. Por favor, intente nuevamente."))
                    elif option == 'q' :
                        self.handle_option('q')
                    else:
                        print(format_info("Opción no válida. Por favor, intente nuevamente."))
                        
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Operación cancelada. Volviendo al menú principal...{Style.RESET_ALL}")
                    continue
        except KeyboardInterrupt:
            # Salida controlada si se presiona Ctrl+C
            print(f"\n{Fore.YELLOW}Saliendo de la aplicación...{Style.RESET_ALL}")
            self.running = False
