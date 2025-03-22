"""
Clase base para todas las vistas de la aplicación.
"""
import os
from colorama import init

# Inicializar colorama para formateo de texto en consola
init(autoreset=True)

class BaseView:
    """
    Clase base que proporciona funcionalidades comunes para todas las vistas.
    """
    
    def __init__(self):
        """
        Inicializa la vista base.
        """
        pass
    
    def clear_screen(self):
        """
        Limpia la pantalla de la consola.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def pause(self):
        """
        Pausa la ejecución hasta que el usuario presione Enter.
        """
        input("Presione Enter para continuar...")
    
    def print_header(self, title):
        """
        Imprime un encabezado formateado.
        
        Args:
            title (str): Título del encabezado
        """
        from colorama import Fore, Style
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 60}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(60)}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}\n")
