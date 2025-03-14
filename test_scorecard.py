"""
Script de prueba para las nuevas funcionalidades de tarjetas de puntuación.
"""
import os
import sys
from colorama import init

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import Database
from src.controllers.scorecard_controller import ScorecardController
from src.controllers.player_controller import PlayerController
from src.controllers.course_controller import CourseController
from src.views.scorecard.scorecard_stats_view import ScorecardStatsView
from src.views.scorecard.scorecard_utils import ScorecardUtils

# Inicializar colorama
init(autoreset=True)

def main():
    """Función principal de prueba"""
    try:
        # Crear directorio de datos si no existe
        os.makedirs('data', exist_ok=True)
        
        # Inicializar la base de datos
        db = Database('data/golf.db')
        
        # Inicializar controladores
        scorecard_controller = ScorecardController(db)
        player_controller = PlayerController(db)
        course_controller = CourseController(db)
        
        # Obtener todas las tarjetas
        scorecards = scorecard_controller.get_scorecards()
        
        print(f"Total de tarjetas: {len(scorecards)}")
        
        # Mostrar detalles de la primera tarjeta si existe
        if scorecards:
            scorecard = scorecards[0]
            print(f"\nDetalles de la tarjeta #{scorecard.id}:")
            print(f"Fecha: {scorecard.date}")
            print(f"Jugador ID: {scorecard.player_id}")
            print(f"Campo ID: {scorecard.course_id}")
            print(f"Total de golpes: {scorecard.total_strokes()}")
            print(f"Total de golpes netos: {scorecard.total_handicap_strokes()}")
            print(f"Total de puntos: {scorecard.total_points()}")
            
            # Obtener información adicional
            player = player_controller.get_player(scorecard.player_id)
            course = course_controller.get_course(scorecard.course_id)
            
            if player:
                print(f"\nJugador: {player.first_name} {player.surname}")
                print(f"Hándicap: {player.handicap}")
            
            if course:
                print(f"\nCampo: {course.name}")
                print(f"Ubicación: {course.location}")
                print(f"Par total: {course.par_total}")
            
            # Usar las utilidades para preparar datos
            scorecard_data = ScorecardUtils.prepare_scorecard_data(
                scorecard, player_controller, course_controller, player, course
            )
            
            print("\nDatos preparados con ScorecardUtils:")
            if 'vs_par' in scorecard_data:
                print(f"Diferencia con el par: {scorecard_data['vs_par_text']}")
            
            if 'vs_handicap_par' in scorecard_data:
                print(f"Diferencia neta con el par: {scorecard_data['vs_handicap_par_text']}")
            
            # Calcular estadísticas
            if course:
                stats = ScorecardUtils.calculate_stats(scorecard, course)
                print("\nEstadísticas:")
                print(f"Eagles o mejor: {stats.get('eagles', 0)}")
                print(f"Birdies: {stats.get('birdies', 0)}")
                print(f"Pares: {stats.get('pars', 0)}")
                print(f"Bogeys: {stats.get('bogeys', 0)}")
                print(f"Doble bogeys: {stats.get('double_bogeys', 0)}")
                print(f"Triple bogeys o peor: {stats.get('others', 0)}")
        
        print("\nPrueba completada con éxito!")
        
    except Exception as e:
        print(f"Error durante la prueba: {str(e)}")

if __name__ == "__main__":
    main()
