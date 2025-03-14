"""
Vista para gestionar la interacción con tarjetas de puntuación.
Este archivo se mantiene por compatibilidad con el código existente,
pero delega toda la funcionalidad a los componentes especializados.
"""
from src.controllers.scorecard_controller import ScorecardController
from src.controllers.player_controller import PlayerController
from src.controllers.course_controller import CourseController
from src.views.player_view import PlayerView
from src.views.course_view import CourseView

# Importar componentes especializados
from src.views.scorecard.scorecard_display import ScorecardDisplayView
from src.views.scorecard.scorecard_edit import ScorecardEditView
from src.views.scorecard.scorecard_filter import ScorecardFilterView
from src.views.scorecard.scorecard_stats import ScorecardStatsView

class ScorecardView:
    """
    Vista para gestionar la interacción con tarjetas de puntuación.
    Esta clase delega la funcionalidad a componentes especializados.
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
        """Muestra el menú principal de tarjetas de puntuación."""
        return self.display_view.show_scorecards()
    
    def show_scorecards(self):
        """Muestra la lista de tarjetas."""
        return self.display_view.show_scorecards()
    
    def add_scorecard(self):
        """Añade una nueva tarjeta."""
        return self.edit_view.add_scorecard()
    
    def modify_scorecard(self, scorecard_id):
        """Modifica una tarjeta existente."""
        return self.edit_view.modify_scorecard(scorecard_id)
    
    def delete_scorecard(self, scorecard_id):
        """Elimina una tarjeta existente."""
        return self.edit_view.delete_scorecard(scorecard_id)
    
    def view_scorecard_details(self, scorecard_id):
        """Muestra los detalles de una tarjeta."""
        return self.display_view.view_scorecard_details(scorecard_id)
    
    def filter_scorecards(self):
        """Filtra tarjetas según criterios."""
        return self.filter_view.filter_scorecards()
    
    def show_statistics(self):
        """Muestra estadísticas de tarjetas."""
        return self.stats_view.show_statistics()
