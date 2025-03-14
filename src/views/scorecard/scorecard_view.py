"""
Vista principal para gestionar la interacción con tarjetas de puntuación.
"""
from src.controllers.scorecard_controller import ScorecardController
from src.controllers.player_controller import PlayerController
from src.controllers.course_controller import CourseController
from src.views.player_view import PlayerView
from src.views.course_view import CourseView
from src.utils.formatters import (
    format_title, format_subtitle, format_table, format_menu_option
)
from src.utils.helpers_simple import (
    clear_screen, pause, get_number_input
)
from src.views.scorecard.scorecard_display import ScorecardDisplayView
from src.views.scorecard.scorecard_edit import ScorecardEditView
from src.views.scorecard.scorecard_filter import ScorecardFilterView
from src.views.scorecard.scorecard_stats import ScorecardStatsView

class ScorecardView:
    """
    Vista principal para gestionar la interacción con tarjetas de puntuación.
    Coordina las diferentes vistas especializadas.
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
        
        # Inicializar vistas especializadas
        self.display_view = ScorecardDisplayView(
            self.controller, self.player_controller, self.course_controller
        )
        self.edit_view = ScorecardEditView(
            self.controller, self.player_controller, self.course_controller
        )
        self.filter_view = ScorecardFilterView(
            self.controller, self.player_controller, self.course_controller
        )
        self.stats_view = ScorecardStatsView(
            self.controller, self.player_controller, self.course_controller
        )
    
    def show_menu(self):
        """
        Muestra el menú principal de tarjetas de puntuación.
        """
        while True:
            clear_screen()
            print(format_title("GESTIÓN DE TARJETAS DE PUNTUACIÓN"))
            
            print(format_menu_option("1", "Ver todas las tarjetas"))
            print(format_menu_option("2", "Añadir nueva tarjeta"))
            print(format_menu_option("3", "Filtrar tarjetas"))
            print(format_menu_option("4", "Estadísticas"))
            print(format_menu_option("0", "Volver al menú principal"))
            
            option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=4, allow_float=False)
            
            if option == 0:
                return
            elif option == 1:
                self.display_view.show_scorecards()
            elif option == 2:
                self.edit_view.add_scorecard()
            elif option == 3:
                self.filter_view.filter_scorecards()
            elif option == 4:
                self.stats_view.show_statistics()
    
    # Métodos de delegación para mantener compatibilidad con código existente
    
    def show_scorecards(self):
        """Muestra la lista de tarjetas."""
        self.display_view.show_scorecards()
    
    def add_scorecard(self):
        """Añade una nueva tarjeta."""
        self.edit_view.add_scorecard()
    
    def modify_scorecard(self, scorecard_id):
        """Modifica una tarjeta existente."""
        self.edit_view.modify_scorecard(scorecard_id)
    
    def delete_scorecard(self, scorecard_id):
        """Elimina una tarjeta existente."""
        self.edit_view.delete_scorecard(scorecard_id)
    
    def view_scorecard_details(self, scorecard_id):
        """Muestra los detalles de una tarjeta."""
        self.display_view.view_scorecard_details(scorecard_id)
    
    def filter_scorecards(self):
        """Filtra tarjetas según criterios."""
        self.filter_view.filter_scorecards()
    
    def show_statistics(self):
        """Muestra estadísticas de tarjetas."""
        self.stats_view.show_statistics()
