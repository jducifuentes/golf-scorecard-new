"""
Vista para mostrar estadísticas de las tarjetas de puntuación.
"""
import os
from colorama import Fore, Style, init
from src.views.scorecard.scorecard_utils import ScorecardUtils

# Inicializar colorama
init(autoreset=True)


class ScorecardStatsView:
    """
    Vista para mostrar estadísticas de tarjetas de puntuación.
    """
    
    def __init__(self, scorecard_controller, player_controller, course_controller):
        """
        Inicializa la vista de estadísticas de tarjetas.
        
        Args:
            scorecard_controller: Controlador de tarjetas
            player_controller: Controlador de jugadores
            course_controller: Controlador de campos
        """
        self.scorecard_controller = scorecard_controller
        self.player_controller = player_controller
        self.course_controller = course_controller
    
    def clear_screen(self):
        """Limpia la pantalla de la consola."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """
        Imprime un encabezado formateado.
        
        Args:
            title (str): Título del encabezado
        """
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 60}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(60)}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}\n")
    
    def show_scorecard_stats(self, scorecard_id):
        """
        Muestra estadísticas detalladas de una tarjeta específica.
        
        Args:
            scorecard_id (int): ID de la tarjeta
            
        Returns:
            bool: True si se mostró correctamente, False en caso contrario
        """
        # Obtener la tarjeta
        scorecard = self.scorecard_controller.get_scorecard(scorecard_id)
        if not scorecard:
            print(f"{Fore.RED}No se encontró la tarjeta con ID {scorecard_id}")
            return False
        
        # Obtener datos relacionados
        player = self.player_controller.get_player(scorecard.player_id)
        course = self.course_controller.get_course(scorecard.course_id)
        
        if not player or not course:
            print(f"{Fore.RED}No se encontraron datos completos para esta tarjeta")
            return False
        
        # Preparar datos
        scorecard_data = ScorecardUtils.prepare_scorecard_data(
            scorecard, self.player_controller, self.course_controller, player, course
        )
        
        # Calcular estadísticas
        stats = ScorecardUtils.calculate_stats(scorecard, course)
        
        # Mostrar encabezado
        self.clear_screen()
        self.print_header(f"Estadísticas de Tarjeta - {player.first_name} {player.surname}")
        
        # Información general
        print(f"{Fore.YELLOW}{Style.BRIGHT}Información General:{Style.RESET_ALL}")
        print(f"  Fecha: {scorecard.date}")
        print(f"  Campo: {course.name} ({course.location})")
        print(f"  Hándicap de juego: {scorecard.playing_handicap}")
        print(f"  Coeficiente aplicado: {scorecard.handicap_coefficient}%")
        
        # Resultados generales
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Resultados:{Style.RESET_ALL}")
        print(f"  Total de golpes: {stats['total_strokes']}")
        
        if 'vs_par' in stats:
            vs_par_text = ScorecardUtils.format_vs_par(stats['vs_par'])
            print(f"  Diferencia con el par: {vs_par_text}")
        
        print(f"  Total de golpes netos: {stats['total_handicap_strokes']}")
        
        if 'vs_handicap_par' in stats:
            vs_handicap_text = ScorecardUtils.format_vs_par(stats['vs_handicap_par'])
            print(f"  Diferencia neta con el par: {vs_handicap_text}")
        
        print(f"  Total de puntos Stableford: {stats['total_points']}")
        
        # Estadísticas detalladas
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Estadísticas por Resultado:{Style.RESET_ALL}")
        print(f"  Eagles o mejor: {stats.get('eagles', 0)}")
        print(f"  Birdies: {stats.get('birdies', 0)}")
        print(f"  Pares: {stats.get('pars', 0)}")
        print(f"  Bogeys: {stats.get('bogeys', 0)}")
        print(f"  Dobles Bogeys: {stats.get('double_bogeys', 0)}")
        print(f"  Triples o peor: {stats.get('others', 0)}")
        
        # Mostrar resultados por hoyo
        self._show_hole_by_hole_results(scorecard, course)
        
        input("\nPresione Enter para continuar...")
        return True
    
    def _show_hole_by_hole_results(self, scorecard, course):
        """
        Muestra los resultados hoyo por hoyo.
        
        Args:
            scorecard: Tarjeta de puntuación
            course: Campo de golf
        """
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Resultados por Hoyo:{Style.RESET_ALL}")
        
        # Encabezados
        print("\n  Hoyo  | Par | Hdcp | Golpes | Neto | Pts | Resultado")
        print("  " + "-" * 50)
        
        # Datos por hoyo
        for i in range(len(scorecard.strokes)):
            if i < len(course.hole_pars) and i < len(course.hole_handicaps):
                hole_num = i + 1
                par = course.hole_pars[i]
                hdcp = course.hole_handicaps[i]
                stroke = scorecard.strokes[i] if i < len(scorecard.strokes) else None
                h_stroke = scorecard.handicap_strokes[i] if i < len(scorecard.handicap_strokes) else None
                point = scorecard.points[i] if i < len(scorecard.points) else None
                
                # Formatear resultados con colores
                stroke_text = ScorecardUtils.format_stroke_result(stroke, par)
                point_text = ScorecardUtils.format_points(point)
                result_name = ScorecardUtils.get_score_name(stroke, par)
                
                print(f"  {hole_num:2d}    | {par:3d} | {hdcp:4d} | {stroke_text:6s} | {h_stroke:4s} | {point_text:3s} | {result_name}")
        
        # Totales
        print("  " + "-" * 50)
        print(f"  Total | {course.par_total:3d} |      | {scorecard.total_strokes():6d} | {scorecard.total_handicap_strokes():4d} | {scorecard.total_points():3d} |")
    
    def show_player_stats(self, player_id):
        """
        Muestra estadísticas acumuladas para un jugador específico.
        
        Args:
            player_id (int): ID del jugador
            
        Returns:
            bool: True si se mostró correctamente, False en caso contrario
        """
        # Obtener el jugador
        player = self.player_controller.get_player(player_id)
        if not player:
            print(f"{Fore.RED}No se encontró el jugador con ID {player_id}")
            return False
        
        # Obtener todas las tarjetas del jugador
        scorecards = self.scorecard_controller.get_scorecards_by_player(player_id)
        if not scorecards:
            print(f"{Fore.RED}No se encontraron tarjetas para {player.first_name} {player.surname}")
            return False
        
        # Estadísticas acumuladas
        total_rounds = len(scorecards)
        total_strokes = 0
        total_points = 0
        total_vs_par = 0
        total_vs_handicap_par = 0
        
        # Contadores para resultados
        eagles = 0
        birdies = 0
        pars = 0
        bogeys = 0
        double_bogeys = 0
        others = 0
        
        # Procesar cada tarjeta
        for scorecard in scorecards:
            course = self.course_controller.get_course(scorecard.course_id)
            if course:
                stats = ScorecardUtils.calculate_stats(scorecard, course)
                
                total_strokes += stats['total_strokes']
                total_points += stats['total_points']
                
                if 'vs_par' in stats:
                    total_vs_par += stats['vs_par']
                
                if 'vs_handicap_par' in stats:
                    total_vs_handicap_par += stats['vs_handicap_par']
                
                # Acumular resultados
                eagles += stats.get('eagles', 0)
                birdies += stats.get('birdies', 0)
                pars += stats.get('pars', 0)
                bogeys += stats.get('bogeys', 0)
                double_bogeys += stats.get('double_bogeys', 0)
                others += stats.get('others', 0)
        
        # Calcular promedios
        avg_strokes = total_strokes / total_rounds if total_rounds > 0 else 0
        avg_points = total_points / total_rounds if total_rounds > 0 else 0
        avg_vs_par = total_vs_par / total_rounds if total_rounds > 0 else 0
        avg_vs_handicap_par = total_vs_handicap_par / total_rounds if total_rounds > 0 else 0
        
        # Mostrar estadísticas
        self.clear_screen()
        self.print_header(f"Estadísticas de {player.first_name} {player.surname}")
        
        print(f"{Fore.YELLOW}{Style.BRIGHT}Información General:{Style.RESET_ALL}")
        print(f"  Hándicap actual: {player.handicap}")
        print(f"  Total de rondas: {total_rounds}")
        
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Promedios:{Style.RESET_ALL}")
        print(f"  Promedio de golpes: {avg_strokes:.2f}")
        print(f"  Promedio vs par: {ScorecardUtils.format_vs_par(avg_vs_par)}")
        print(f"  Promedio neto vs par: {ScorecardUtils.format_vs_par(avg_vs_handicap_par)}")
        print(f"  Promedio de puntos Stableford: {avg_points:.2f}")
        
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Totales:{Style.RESET_ALL}")
        print(f"  Eagles o mejor: {eagles} ({eagles/total_rounds:.2f} por ronda)")
        print(f"  Birdies: {birdies} ({birdies/total_rounds:.2f} por ronda)")
        print(f"  Pares: {pars} ({pars/total_rounds:.2f} por ronda)")
        print(f"  Bogeys: {bogeys} ({bogeys/total_rounds:.2f} por ronda)")
        print(f"  Dobles Bogeys: {double_bogeys} ({double_bogeys/total_rounds:.2f} por ronda)")
        print(f"  Triples o peor: {others} ({others/total_rounds:.2f} por ronda)")
        
        # Mostrar últimas 5 rondas
        self._show_recent_rounds(player_id, 5)
        
        input("\nPresione Enter para continuar...")
        return True
    
    def _show_recent_rounds(self, player_id, limit=5):
        """
        Muestra las rondas más recientes de un jugador.
        
        Args:
            player_id (int): ID del jugador
            limit (int): Número máximo de rondas a mostrar
        """
        # Obtener tarjetas recientes
        scorecards = self.scorecard_controller.get_scorecards_by_player(player_id, limit=limit)
        
        if not scorecards:
            return
        
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Rondas Recientes:{Style.RESET_ALL}")
        print("\n  Fecha     | Campo                | Golpes | vs Par | Neto  | Puntos")
        print("  " + "-" * 70)
        
        for scorecard in scorecards:
            course = self.course_controller.get_course(scorecard.course_id)
            if course:
                stats = ScorecardUtils.calculate_stats(scorecard, course)
                
                date = scorecard.date
                course_name = course.name[:20]  # Limitar longitud
                strokes = stats['total_strokes']
                vs_par = ScorecardUtils.format_vs_par(stats.get('vs_par', 0))
                net_strokes = stats['total_handicap_strokes']
                points = stats['total_points']
                
                print(f"  {date:10s} | {course_name:20s} | {strokes:6d} | {vs_par:6s} | {net_strokes:5d} | {points:6d}")
    
    def show_menu(self, player_id=None):
        """
        Muestra el menú de estadísticas.
        
        Args:
            player_id (int, optional): ID del jugador preseleccionado
        """
        while True:
            self.clear_screen()
            self.print_header("Menú de Estadísticas")
            
            print("1. Ver estadísticas de una tarjeta específica")
            print("2. Ver estadísticas de un jugador")
            print("0. Volver al menú principal")
            
            option = input("\nSeleccione una opción: ")
            
            if option == "1":
                scorecard_id = input("Ingrese el ID de la tarjeta: ")
                try:
                    self.show_scorecard_stats(int(scorecard_id))
                except ValueError:
                    print(f"{Fore.RED}ID de tarjeta inválido")
                    input("Presione Enter para continuar...")
            
            elif option == "2":
                if player_id:
                    self.show_player_stats(player_id)
                else:
                    player_id_input = input("Ingrese el ID del jugador: ")
                    try:
                        self.show_player_stats(int(player_id_input))
                    except ValueError:
                        print(f"{Fore.RED}ID de jugador inválido")
                        input("Presione Enter para continuar...")
            
            elif option == "0":
                break
            
            else:
                print(f"{Fore.RED}Opción inválida")
                input("Presione Enter para continuar...")
