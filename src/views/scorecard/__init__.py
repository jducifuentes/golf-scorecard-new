"""
Paquete para la vista de tarjetas de puntuación.
"""
from src.views.scorecard.scorecard_view import ScorecardView
from src.views.scorecard.scorecard_display import ScorecardDisplayView
from src.views.scorecard.scorecard_edit import ScorecardEditView
from src.views.scorecard.scorecard_filter import ScorecardFilterView
from src.views.scorecard.scorecard_stats import ScorecardStatsView

__all__ = [
    'ScorecardView',
    'ScorecardDisplayView',
    'ScorecardEditView',
    'ScorecardFilterView',
    'ScorecardStatsView'
]
