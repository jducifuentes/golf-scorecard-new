"""
Vista para mostrar estadísticas de las tarjetas de puntuación.
"""
import os
from colorama import Fore, Style
from src.views.base_view import BaseView
from src.views.utils import format_title, format_info, clear_screen, pause, format_table
from src.views.scorecard.scorecard_utils import ScorecardUtils


class ScorecardStatsView(BaseView):
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
        super().__init__()
        self.scorecard_controller = scorecard_controller
        self.player_controller = player_controller
        self.course_controller = course_controller
    
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
            pause()
            return False
        
        # Obtener el jugador y el campo
        player = self.player_controller.get_player(scorecard.player_id)
        course = self.course_controller.get_course(scorecard.course_id)
        
        if not player or not course:
            print(f"{Fore.RED}No se encontró el jugador o el campo asociado a la tarjeta")
            pause()
            return False
        
        # Mostrar información general
        clear_screen()
        print(format_title(f"ESTADÍSTICAS DE TARJETA #{scorecard_id}"))
        
        print(f"\n{Fore.CYAN}Información general:{Style.RESET_ALL}")
        print(f"  Jugador: {player.full_name}")
        print(f"  Campo: {course.name}")
        print(f"  Fecha: {scorecard.date}")
        print(f"  Handicap de juego: {scorecard.playing_handicap}")
        
        # Calcular estadísticas básicas
        total_strokes = sum(scorecard.strokes) if scorecard.strokes else 0
        
        # Asegurarse de que course.hole_pars existe y es una lista
        if hasattr(course, 'hole_pars') and isinstance(course.hole_pars, list) and course.hole_pars:
            total_par = sum(course.hole_pars)
        else:
            total_par = course.par_total if hasattr(course, 'par_total') else 72
            
        vs_par = total_strokes - total_par
        vs_par_str = f"+{vs_par}" if vs_par > 0 else str(vs_par)
        
        print(f"\n{Fore.CYAN}Estadísticas básicas:{Style.RESET_ALL}")
        print(f"  Total golpes: {total_strokes}")
        print(f"  Par del campo: {total_par}")
        print(f"  Resultado vs Par: {vs_par_str}")
        
        if scorecard.handicap_strokes:
            total_handicap_strokes = sum(scorecard.handicap_strokes)
            vs_par_net = total_handicap_strokes - total_par
            vs_par_net_str = f"+{vs_par_net}" if vs_par_net > 0 else str(vs_par_net)
            print(f"  Total golpes netos: {total_handicap_strokes}")
            print(f"  Resultado neto vs Par: {vs_par_net_str}")
        
        if scorecard.points:
            total_points = sum(scorecard.points)
            print(f"  Total puntos Stableford: {total_points}")
        
        # Analizar rendimiento por tipo de hoyo
        if hasattr(course, 'hole_pars') and isinstance(course.hole_pars, list) and course.hole_pars:
            par3_indices = [i for i, par in enumerate(course.hole_pars) if par == 3]
            par4_indices = [i for i, par in enumerate(course.hole_pars) if par == 4]
            par5_indices = [i for i, par in enumerate(course.hole_pars) if par == 5]
            
            par3_strokes = sum(scorecard.strokes[i] for i in par3_indices if i < len(scorecard.strokes)) if par3_indices else 0
            par4_strokes = sum(scorecard.strokes[i] for i in par4_indices if i < len(scorecard.strokes)) if par4_indices else 0
            par5_strokes = sum(scorecard.strokes[i] for i in par5_indices if i < len(scorecard.strokes)) if par5_indices else 0
            
            par3_total = sum(course.hole_pars[i] for i in par3_indices) if par3_indices else 0
            par4_total = sum(course.hole_pars[i] for i in par4_indices) if par4_indices else 0
            par5_total = sum(course.hole_pars[i] for i in par5_indices) if par5_indices else 0
            
            par3_diff = par3_strokes - par3_total if par3_indices else 0
            par4_diff = par4_strokes - par4_total if par4_indices else 0
            par5_diff = par5_strokes - par5_total if par5_indices else 0
            
            par3_diff_str = f"+{par3_diff}" if par3_diff > 0 else str(par3_diff)
            par4_diff_str = f"+{par4_diff}" if par4_diff > 0 else str(par4_diff)
            par5_diff_str = f"+{par5_diff}" if par5_diff > 0 else str(par5_diff)
            
            print(f"\n{Fore.CYAN}Rendimiento por tipo de hoyo:{Style.RESET_ALL}")
            if par3_indices:
                print(f"  Par 3 ({len(par3_indices)} hoyos): {par3_strokes} golpes ({par3_diff_str})")
            if par4_indices:
                print(f"  Par 4 ({len(par4_indices)} hoyos): {par4_strokes} golpes ({par4_diff_str})")
            if par5_indices:
                print(f"  Par 5 ({len(par5_indices)} hoyos): {par5_strokes} golpes ({par5_diff_str})")
        
        # Contar resultados por tipo
        eagles = sum(1 for i, strokes in enumerate(scorecard.strokes) if strokes == course.hole_pars[i] - 2)
        birdies = sum(1 for i, strokes in enumerate(scorecard.strokes) if strokes == course.hole_pars[i] - 1)
        pars = sum(1 for i, strokes in enumerate(scorecard.strokes) if strokes == course.hole_pars[i])
        bogeys = sum(1 for i, strokes in enumerate(scorecard.strokes) if strokes == course.hole_pars[i] + 1)
        double_bogeys = sum(1 for i, strokes in enumerate(scorecard.strokes) if strokes == course.hole_pars[i] + 2)
        others = sum(1 for i, strokes in enumerate(scorecard.strokes) if strokes > course.hole_pars[i] + 2)
        
        print(f"\n{Fore.CYAN}Distribución de resultados:{Style.RESET_ALL}")
        print(f"  Eagles o mejor: {eagles}")
        print(f"  Birdies: {birdies}")
        print(f"  Pares: {pars}")
        print(f"  Bogeys: {bogeys}")
        print(f"  Doble Bogeys: {double_bogeys}")
        print(f"  Triple Bogey o peor: {others}")
        
        # Mostrar detalles por hoyo
        self.show_hole_details(scorecard, course)
        
        pause()
        return True
    
    def show_hole_details(self, scorecard, course):
        """
        Muestra los detalles de cada hoyo de la tarjeta.
        
        Args:
            scorecard: Tarjeta a mostrar
            course: Campo asociado a la tarjeta
        """
        clear_screen()
        print(format_title(f"DETALLES POR HOYO - TARJETA #{scorecard.id}"))
        
        # Mostrar información básica
        player = self.player_controller.get_player(scorecard.player_id)
        if player:
            print(f"\n{Fore.CYAN}Jugador: {player.first_name} {player.surname}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}Campo: {course.name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Fecha: {scorecard.date}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Hándicap de juego: {scorecard.playing_handicap or 'N/A'}{Style.RESET_ALL}")
        
        # Mostrar tabla de detalles
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Detalles por Hoyo:{Style.RESET_ALL}")
        
        # Preparar datos para la tabla
        headers = ["Hoyo", "Hdcp", "Par", "Golpes", "Puntos", "Resultado"]
        table_data = []
        
        for i, stroke in enumerate(scorecard.strokes):
            if i < len(course.hole_pars) and i < len(course.hole_handicaps):
                hole_num = i + 1
                par = course.hole_pars[i]
                hole_handicap = course.hole_handicaps[i]
                
                # Calcular golpes extra por hándicap para este hoyo
                extra_strokes = 0
                if scorecard.playing_handicap is not None:
                    if scorecard.playing_handicap >= hole_handicap:
                        extra_strokes += 1
                    if scorecard.playing_handicap >= hole_handicap + 18:
                        extra_strokes += 1
                    if scorecard.playing_handicap >= hole_handicap + 36:
                        extra_strokes += 1
                
                # Mostrar golpes extra como asteriscos entre paréntesis
                par_text = f"{par}"
                if extra_strokes > 0:
                    par_text += f" ({'*' * extra_strokes})"
                
                # Obtener puntos si están disponibles
                points = scorecard.points[i] if hasattr(scorecard, 'points') and i < len(scorecard.points) else "-"
                
                # Formatear golpes y puntos con colores
                stroke_text = ScorecardUtils.format_stroke_result(
                    stroke, par, 
                    playing_handicap=scorecard.playing_handicap, 
                    hole_handicap=hole_handicap
                )
                points_text = ScorecardUtils.format_points(points) if points != "-" else "-"
                
                # Calcular resultado
                if stroke is not None and par is not None:
                    # Calcular resultado neto (sin descontar golpes extra)
                    diff = stroke - par
                    
                    if diff < 0:
                        result = f"{Fore.LIGHTBLUE_EX}Bajo par{Style.RESET_ALL}"
                    elif diff == 0:
                        result = f"{Fore.LIGHTCYAN_EX}Par{Style.RESET_ALL}"
                    elif diff == 1:
                        result = f"{Fore.GREEN}Bogey{Style.RESET_ALL}"
                    elif diff == 2:
                        result = f"{Fore.YELLOW}Doble Bogey{Style.RESET_ALL}"
                    else:
                        result = f"{Fore.RED}Triple Bogey o peor{Style.RESET_ALL}"
                else:
                    result = "-"
                
                # Añadir fila a la tabla
                table_data.append([
                    hole_num,
                    hole_handicap,
                    par_text,
                    stroke_text,
                    points_text,
                    result
                ])
        
        # Añadir fila de totales
        table_data.append([
            "Total",
            "",
            course.par_total,
            scorecard.total_strokes(),
            scorecard.total_points() if hasattr(scorecard, 'total_points') else '-',
            ""
        ])
        
        # Mostrar tabla formateada
        print("\n" + format_table(headers, table_data, highlight_last_row=True))
        
        pause()
    
    def show_player_stats(self):
        """
        Muestra estadísticas acumuladas para un jugador específico.
        
        Returns:
            bool: True si se mostró correctamente, False en caso contrario
        """
        # Obtener el jugador
        player_id_input = input("Ingrese el ID del jugador: ")
        try:
            player_id = int(player_id_input)
        except ValueError:
            print(f"{Fore.RED}ID de jugador inválido")
            pause()
            return False
        
        player = self.player_controller.get_player(player_id)
        if not player:
            print(f"{Fore.RED}No se encontró el jugador con ID {player_id}")
            pause()
            return False
        
        # Obtener todas las tarjetas del jugador
        scorecards = self.scorecard_controller.get_player_scorecards(player_id)
        
        if not scorecards:
            print(f"{Fore.RED}El jugador no tiene tarjetas registradas")
            pause()
            return False
        
        # Mostrar información general
        clear_screen()
        print(format_title(f"ESTADÍSTICAS DE {player.full_name.upper()}"))
        
        # Calcular estadísticas básicas
        total_rounds = len(scorecards)
        total_strokes = 0
        total_par = 0
        total_vs_par = 0
        
        # Contadores para tipos de resultados
        total_eagles = 0
        total_birdies = 0
        total_pars = 0
        total_bogeys = 0
        total_double_bogeys = 0
        total_others = 0
        
        # Rendimiento por tipo de hoyo
        par3_strokes = 0
        par3_total = 0
        par4_strokes = 0
        par4_total = 0
        par5_strokes = 0
        par5_total = 0
        
        # Procesar cada tarjeta
        for scorecard in scorecards:
            course = self.course_controller.get_course(scorecard.course_id)
            if not course:
                continue
            
            # Estadísticas básicas
            card_strokes = sum(scorecard.strokes) if scorecard.strokes else 0
            
            # Asegurarse de que course.hole_pars existe y es una lista
            if hasattr(course, 'hole_pars') and isinstance(course.hole_pars, list) and course.hole_pars:
                card_par = sum(course.hole_pars)
            else:
                card_par = course.par_total if hasattr(course, 'par_total') else 72
                
            total_strokes += card_strokes
            total_par += card_par
            total_vs_par += (card_strokes - card_par)
            
            # Contar resultados por tipo
            eagles = sum(1 for i, strokes in enumerate(scorecard.strokes) if strokes == course.hole_pars[i] - 2)
            birdies = sum(1 for i, strokes in enumerate(scorecard.strokes) if strokes == course.hole_pars[i] - 1)
            pars = sum(1 for i, strokes in enumerate(scorecard.strokes) if strokes == course.hole_pars[i])
            bogeys = sum(1 for i, strokes in enumerate(scorecard.strokes) if strokes == course.hole_pars[i] + 1)
            double_bogeys = sum(1 for i, strokes in enumerate(scorecard.strokes) if strokes == course.hole_pars[i] + 2)
            others = sum(1 for i, strokes in enumerate(scorecard.strokes) if strokes > course.hole_pars[i] + 2)
            
            total_eagles += eagles
            total_birdies += birdies
            total_pars += pars
            total_bogeys += bogeys
            total_double_bogeys += double_bogeys
            total_others += others
            
            # Rendimiento por tipo de hoyo
            if hasattr(course, 'hole_pars') and isinstance(course.hole_pars, list) and course.hole_pars:
                par3_indices = [i for i, par in enumerate(course.hole_pars) if par == 3]
                par4_indices = [i for i, par in enumerate(course.hole_pars) if par == 4]
                par5_indices = [i for i, par in enumerate(course.hole_pars) if par == 5]
                
                par3_strokes += sum(scorecard.strokes[i] for i in par3_indices if i < len(scorecard.strokes)) if par3_indices else 0
                par4_strokes += sum(scorecard.strokes[i] for i in par4_indices if i < len(scorecard.strokes)) if par4_indices else 0
                par5_strokes += sum(scorecard.strokes[i] for i in par5_indices if i < len(scorecard.strokes)) if par5_indices else 0
                
                par3_total += sum(course.hole_pars[i] for i in par3_indices) if par3_indices else 0
                par4_total += sum(course.hole_pars[i] for i in par4_indices) if par4_indices else 0
                par5_total += sum(course.hole_pars[i] for i in par5_indices) if par5_indices else 0
        
        # Calcular promedios
        avg_strokes = total_strokes / total_rounds
        avg_vs_par = total_vs_par / total_rounds
        avg_vs_par_str = f"+{avg_vs_par:.1f}" if avg_vs_par > 0 else f"{avg_vs_par:.1f}"
        
        # Mostrar estadísticas generales
        print(f"\n{Fore.CYAN}Estadísticas generales:{Style.RESET_ALL}")
        print(f"  Total de vueltas: {total_rounds}")
        print(f"  Promedio de golpes: {avg_strokes:.1f}")
        print(f"  Promedio vs Par: {avg_vs_par_str}")
        
        # Mostrar distribución de resultados
        print(f"\n{Fore.CYAN}Distribución de resultados:{Style.RESET_ALL}")
        print(f"  Eagles o mejor: {total_eagles} ({total_eagles / total_rounds:.1f} por vuelta)")
        print(f"  Birdies: {total_birdies} ({total_birdies / total_rounds:.1f} por vuelta)")
        print(f"  Pares: {total_pars} ({total_pars / total_rounds:.1f} por vuelta)")
        print(f"  Bogeys: {total_bogeys} ({total_bogeys / total_rounds:.1f} por vuelta)")
        print(f"  Doble Bogeys: {total_double_bogeys} ({total_double_bogeys / total_rounds:.1f} por vuelta)")
        print(f"  Triple Bogey o peor: {total_others} ({total_others / total_rounds:.1f} por vuelta)")
        
        # Mostrar rendimiento por tipo de hoyo
        print(f"\n{Fore.CYAN}Rendimiento por tipo de hoyo:{Style.RESET_ALL}")
        if par3_total > 0:
            par3_diff = par3_strokes - par3_total
            par3_avg = par3_diff / (par3_total / 3)  # Dividir por el número de hoyos par 3
            par3_avg_str = f"+{par3_avg:.1f}" if par3_avg > 0 else f"{par3_avg:.1f}"
            print(f"  Par 3: {par3_avg_str} sobre par en promedio")
        
        if par4_total > 0:
            par4_diff = par4_strokes - par4_total
            par4_avg = par4_diff / (par4_total / 4)  # Dividir por el número de hoyos par 4
            par4_avg_str = f"+{par4_avg:.1f}" if par4_avg > 0 else f"{par4_avg:.1f}"
            print(f"  Par 4: {par4_avg_str} sobre par en promedio")
        
        if par5_total > 0:
            par5_diff = par5_strokes - par5_total
            par5_avg = par5_diff / (par5_total / 5)  # Dividir por el número de hoyos par 5
            par5_avg_str = f"+{par5_avg:.1f}" if par5_avg > 0 else f"{par5_avg:.1f}"
            print(f"  Par 5: {par5_avg_str} sobre par en promedio")
        
        # Mostrar historial de tarjetas
        print(f"\n{Fore.CYAN}Historial de tarjetas:{Style.RESET_ALL}")
        print(f"  {'Fecha':10s} | {'Campo':20s} | {'Golpes':6s} | {'vs Par':6s} | {'Neto':5s} | {'Puntos':6s}")
        print("  " + "-" * 65)
        
        # Ordenar tarjetas por fecha (más recientes primero)
        scorecards.sort(key=lambda x: x.date, reverse=True)
        
        for scorecard in scorecards:
            course = self.course_controller.get_course(scorecard.course_id)
            if not course:
                continue
            
            date = scorecard.date
            course_name = course.name
            strokes = sum(scorecard.strokes) if scorecard.strokes else 0
            
            # Asegurarse de que course.hole_pars existe y es una lista
            if hasattr(course, 'hole_pars') and isinstance(course.hole_pars, list) and course.hole_pars:
                par = sum(course.hole_pars)
            else:
                par = course.par_total if hasattr(course, 'par_total') else 72
                
            vs_par = strokes - par
            vs_par_str = f"+{vs_par}" if vs_par > 0 else str(vs_par)
            
            net_strokes = "-"
            if scorecard.handicap_strokes:
                net_strokes = strokes - sum(scorecard.handicap_strokes)
            
            points = "-"
            if scorecard.points:
                points = sum(scorecard.points)
                
            print(f"  {date:10s} | {course_name:20s} | {strokes:6d} | {vs_par_str:6s} | {net_strokes:5} | {points:6}")
        
        pause()
        return True
    
    def show_course_stats(self):
        """
        Muestra estadísticas acumuladas para un campo específico.
        
        Returns:
            bool: True si se mostró correctamente, False en caso contrario
        """
        # Implementación pendiente
        print(f"{Fore.YELLOW}Funcionalidad en desarrollo.{Style.RESET_ALL}")
        pause()
        return False
    
    def show_menu(self):
        """
        Muestra el menú principal de estadísticas.
        """
        while True:
            clear_screen()
            print(format_title("ESTADÍSTICAS"))
            
            print("\nOpciones disponibles:")
            print("  1. Estadísticas de una tarjeta específica")
            print("  2. Estadísticas por jugador")
            print("  3. Estadísticas por campo")
            print("  0. Volver")
            
            option = input("\nSeleccione una opción: ")
            
            if option == "1":
                # Estadísticas de una tarjeta específica
                clear_screen()
                print(format_title("ESTADÍSTICAS DE TARJETA"))
                
                scorecard_id = input("\nIngrese el ID de la tarjeta (0 para cancelar): ")
                
                if scorecard_id == "0":
                    continue
                
                try:
                    self.show_scorecard_stats(int(scorecard_id))
                except ValueError:
                    print(f"{Fore.RED}ID inválido. Debe ingresar un número entero.{Style.RESET_ALL}")
                    pause()
            
            elif option == "2":
                # Estadísticas por jugador
                self.show_player_stats()
            
            elif option == "3":
                # Estadísticas por campo
                self.show_course_stats()
            
            elif option == "0":
                return
            
            else:
                print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")
                pause()
