"""
Vista principal para gestionar tarjetas de puntuación.
"""
from colorama import Fore, Style
from src.controllers.scorecard_controller import ScorecardController
from src.controllers.player_controller import PlayerController
from src.controllers.course_controller import CourseController
from src.views.base_view import BaseView
from src.views.utils import format_title, format_info, clear_screen, pause
from src.utils.formatters import format_menu_option, format_error
from src.utils.helpers_simple import get_number_input
from src.views.scorecard.scorecard_list_view import ScorecardListView
from src.views.scorecard.scorecard_edit_view import ScorecardEditView
from src.views.scorecard.scorecard_create_view import ScorecardCreateView
from src.views.scorecard.scorecard_export_view import ScorecardExportView


class ScorecardView(BaseView):
    """
    Vista principal para gestionar tarjetas de puntuación.
    """
    
    def __init__(self, db):
        """
        Inicializa la vista de tarjetas.
        
        Args:
            db: Instancia de la base de datos
        """
        super().__init__()
        self.db = db
        self.scorecard_controller = ScorecardController(db)
        self.player_controller = PlayerController(db)
        self.course_controller = CourseController(db)
        
        # Inicializar vistas específicas
        self.list_view = ScorecardListView(
            self.scorecard_controller,
            self.player_controller,
            self.course_controller
        )
        self.edit_view = ScorecardEditView(
            self.scorecard_controller,
            self.player_controller,
            self.course_controller
        )
        self.create_view = ScorecardCreateView(
            self.scorecard_controller,
            self.player_controller,
            self.course_controller
        )
        self.export_view = ScorecardExportView(
            self.scorecard_controller,
            self.player_controller,
            self.course_controller
        )
    
    def show_menu(self):
        """
        Muestra el menú principal de tarjetas.
        """
        while True:
            clear_screen()
            print(format_title("GESTIÓN DE TARJETAS"))
            
            print(f"\n{Fore.YELLOW}Opciones:{Style.RESET_ALL}")
            print(format_menu_option("1", "Ver todas las tarjetas"))
            print(format_menu_option("2", "Buscar tarjetas"))
            print(format_menu_option("3", "Crear nueva tarjeta"))
            print(format_menu_option("4", "Exportar tarjetas"))
            print(format_menu_option("0", "Volver al menú principal"))
            
            option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=4, allow_float=False)
            
            if option == 0:
                break
            elif option == 1:
                selected_scorecard = self.show_all_scorecards()
                if selected_scorecard:
                    self.edit_view.show_scorecard_options(selected_scorecard)
            elif option == 2:
                selected_scorecard = self.search_scorecards()
                if selected_scorecard:
                    self.edit_view.show_scorecard_options(selected_scorecard)
            elif option == 3:
                self.create_scorecard()
            elif option == 4:
                self.export_view.show_export_menu()
            else:
                print(format_error("Opción inválida."))
                pause()
    
    def show_all_scorecards(self):
        """
        Muestra todas las tarjetas de puntuación.
        
        Returns:
            Scorecard: La tarjeta seleccionada o None si se cancela
        """
        return self.list_view.show_all_scorecards()
    
    def search_scorecards(self):
        """
        Busca tarjetas según criterios.
        
        Returns:
            Scorecard: La tarjeta seleccionada o None si se cancela
        """
        return self.list_view.search_scorecards()
    
    def create_scorecard(self):
        """
        Crea una nueva tarjeta de puntuación.
        
        Returns:
            bool: True si se creó correctamente, False en caso contrario
        """
        return self.create_view.create_scorecard()
