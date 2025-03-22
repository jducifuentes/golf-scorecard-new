"""
Vista para la edición de tarjetas de puntuación.
"""
from colorama import Fore, Style
from src.views.base_view import BaseView
from src.views.utils import format_title, format_info, clear_screen, pause, format_table
from src.views.scorecard.scorecard_utils import ScorecardUtils


class ScorecardEditView(BaseView):
    """
    Vista para editar tarjetas de puntuación.
    """
    
    def __init__(self, scorecard_controller, player_controller, course_controller):
        """
        Inicializa la vista de edición de tarjetas.
        
        Args:
            scorecard_controller: Controlador de tarjetas
            player_controller: Controlador de jugadores
            course_controller: Controlador de campos
        """
        super().__init__()
        self.scorecard_controller = scorecard_controller
        self.player_controller = player_controller
        self.course_controller = course_controller
    
    def display_scorecard_details(self, scorecard):
        """
        Muestra los detalles de una tarjeta.
        
        Args:
            scorecard: Tarjeta a mostrar
        """
        clear_screen()
        print(format_title(f"DETALLES DE TARJETA #{scorecard.id}"))
        
        # Obtener información del jugador y campo
        player = self.player_controller.get_player(scorecard.player_id)
        course = self.course_controller.get_course(scorecard.course_id)
        
        # Preparar datos para visualización
        scorecard_data = ScorecardUtils.prepare_scorecard_data(
            scorecard, self.player_controller, self.course_controller, player, course
        )
        
        # Mostrar información básica
        print(f"\n{Fore.CYAN}{Style.BRIGHT}Información Básica:{Style.RESET_ALL}")
        print(f"  Jugador: {scorecard_data['player_name']}")
        print(f"  Campo: {scorecard_data['course_name']}")
        print(f"  Fecha: {scorecard.date}")
        print(f"  Hándicap de juego: {scorecard.playing_handicap or 'N/A'}")
        print(f"  Coeficiente de hándicap: {scorecard.handicap_coefficient}%")
        
        # Mostrar resultados
        print(f"\n{Fore.GREEN}{Style.BRIGHT}Resultados:{Style.RESET_ALL}")
        print(f"  Total golpes: {scorecard_data['total_strokes']}")
        
        if 'total_points' in scorecard_data:
            print(f"  Total puntos: {scorecard_data['total_points']}")
        
        if 'vs_par' in scorecard_data:
            print(f"  Diferencia con par: {scorecard_data['vs_par_text']}")
        
        # Mostrar detalles por hoyo
        if course and scorecard.strokes:
            print(f"\n{Fore.YELLOW}{Style.BRIGHT}Detalles por Hoyo:{Style.RESET_ALL}")
            
            # Preparar datos para la tabla
            headers = ["Hoyo", "Hdcp", "Par", "Golpes", "Puntos"]
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
                    
                    # Añadir fila a la tabla
                    table_data.append([
                        hole_num,
                        hole_handicap,
                        par_text,
                        stroke_text,
                        points_text
                    ])
            
            # Añadir fila de totales
            table_data.append([
                "Total",
                "",
                course.par_total,
                scorecard.total_strokes(),
                scorecard.total_points() if hasattr(scorecard, 'total_points') else '-'
            ])
            
            # Mostrar tabla formateada
            print("\n" + format_table(headers, table_data, highlight_last_row=True))
        
        pause()
    
    def edit_scorecard(self, scorecard):
        """
        Edita una tarjeta existente.
        
        Args:
            scorecard (Scorecard): Tarjeta a editar
            
        Returns:
            bool: True si se editó correctamente, False en caso contrario
        """
        editing = True
        
        while editing:
            clear_screen()
            print(format_title(f"EDITAR TARJETA #{scorecard.id}"))
            
            # Obtener información del jugador y campo
            player = self.player_controller.get_player(scorecard.player_id)
            course = self.course_controller.get_course(scorecard.course_id)
            
            if not player or not course:
                print(f"{Fore.RED}No se pudo obtener la información completa de la tarjeta.{Style.RESET_ALL}")
                pause()
                return False
            
            # Mostrar información actual
            print(f"\n{Fore.CYAN}Información actual:{Style.RESET_ALL}")
            print(f"  Jugador: {player.first_name} {player.surname}")
            print(f"  Campo: {course.name}")
            print(f"  Fecha: {scorecard.date}")
            print(f"  Hándicap de juego: {scorecard.playing_handicap}")
            
            # Mostrar golpes actuales
            print(f"\n{Fore.YELLOW}Golpes actuales por hoyo:{Style.RESET_ALL}")
            
            for i, par in enumerate(course.hole_pars):
                hole_num = i + 1
                stroke = scorecard.strokes[i] if i < len(scorecard.strokes) else "-"
                
                # Formatear golpes con colores
                stroke_text = ScorecardUtils.format_stroke_result(stroke, par) if stroke != "-" else "-"
                
                print(f"  Hoyo {hole_num} (Par {par}): {stroke_text}")
            
            # Opciones de edición
            print(f"\n{Fore.GREEN}Opciones de edición:{Style.RESET_ALL}")
            print("  1. Editar golpes por hoyo")
            print("  2. Editar fecha")
            print("  3. Editar hándicap de juego")
            print("  4. Guardar y salir")
            print("  0. Cancelar")
            
            option = input("\nSeleccione una opción: ")
            
            if option == "1":
                # Editar golpes por hoyo
                clear_screen()
                print(format_title("EDITAR GOLPES"))
                
                print(f"\n{Fore.CYAN}Instrucciones:{Style.RESET_ALL}")
                print("  - Ingrese el número de golpes para cada hoyo")
                print("  - Deje en blanco para mantener el valor actual")
                print("  - Ingrese 'x' para cancelar\n")
                
                new_strokes = scorecard.strokes.copy()
                
                for i, par in enumerate(course.hole_pars):
                    hole_num = i + 1
                    current = new_strokes[i] if i < len(new_strokes) else "-"
                    
                    # Formatear golpes con colores
                    current_text = ScorecardUtils.format_stroke_result(current, par) if current != "-" else "-"
                    
                    while True:
                        stroke_input = input(f"  Hoyo {hole_num} (Par {par}, Actual: {current_text}): ")
                        
                        if stroke_input.lower() == 'x':
                            return self.edit_scorecard(scorecard)
                        
                        if stroke_input == "":
                            # Mantener valor actual
                            break
                        
                        try:
                            stroke = int(stroke_input)
                            if stroke <= 0:
                                print(f"{Fore.RED}El número de golpes debe ser positivo.{Style.RESET_ALL}")
                                continue
                            
                            # Actualizar valor
                            if i < len(new_strokes):
                                new_strokes[i] = stroke
                            else:
                                new_strokes.append(stroke)
                            break
                        except ValueError:
                            print(f"{Fore.RED}Valor inválido. Debe ingresar un número entero.{Style.RESET_ALL}")
                
                # Actualizar tarjeta
                success, message = self.scorecard_controller.update_scorecard(
                    scorecard.id,
                    player_id=scorecard.player_id,
                    course_id=scorecard.course_id,
                    date=scorecard.date,
                    strokes=new_strokes,
                    playing_handicap=scorecard.playing_handicap,
                    handicap_coefficient=scorecard.handicap_coefficient
                )
                
                if success:
                    print(f"{Fore.GREEN}Tarjeta actualizada correctamente.{Style.RESET_ALL}")
                    # Recargar tarjeta con los nuevos datos
                    scorecard = self.scorecard_controller.get_scorecard(scorecard.id)
                else:
                    print(f"{Fore.RED}Error al actualizar la tarjeta: {message}{Style.RESET_ALL}")
                
                pause()
            
            elif option == "2":
                # Editar fecha
                clear_screen()
                print(format_title("EDITAR FECHA"))
                
                print(f"\nFecha actual: {scorecard.date}")
                new_date = input("Nueva fecha (YYYY-MM-DD, deje en blanco para mantener): ")
                
                if new_date:
                    success, message = self.scorecard_controller.update_scorecard(
                        scorecard.id,
                        player_id=scorecard.player_id,
                        course_id=scorecard.course_id,
                        date=new_date,
                        strokes=scorecard.strokes,
                        playing_handicap=scorecard.playing_handicap,
                        handicap_coefficient=scorecard.handicap_coefficient
                    )
                    
                    if success:
                        print(f"{Fore.GREEN}Fecha actualizada correctamente.{Style.RESET_ALL}")
                        # Recargar tarjeta con los nuevos datos
                        scorecard = self.scorecard_controller.get_scorecard(scorecard.id)
                    else:
                        print(f"{Fore.RED}Error al actualizar la fecha: {message}{Style.RESET_ALL}")
                
                pause()
            
            elif option == "3":
                # Editar hándicap de juego
                clear_screen()
                print(format_title("EDITAR HÁNDICAP DE JUEGO"))
                
                print(f"\nHándicap de juego actual: {scorecard.playing_handicap}")
                
                while True:
                    handicap_input = input("Nuevo hándicap de juego (deje en blanco para mantener): ")
                    
                    if handicap_input == "":
                        break
                    
                    try:
                        handicap = float(handicap_input)
                        
                        success, message = self.scorecard_controller.update_scorecard(
                            scorecard.id,
                            player_id=scorecard.player_id,
                            course_id=scorecard.course_id,
                            date=scorecard.date,
                            strokes=scorecard.strokes,
                            playing_handicap=handicap,
                            handicap_coefficient=scorecard.handicap_coefficient
                        )
                        
                        if success:
                            print(f"{Fore.GREEN}Hándicap actualizado correctamente.{Style.RESET_ALL}")
                            # Recargar tarjeta con los nuevos datos
                            scorecard = self.scorecard_controller.get_scorecard(scorecard.id)
                        else:
                            print(f"{Fore.RED}Error al actualizar el hándicap: {message}{Style.RESET_ALL}")
                        
                        break
                    except ValueError:
                        print(f"{Fore.RED}Valor inválido. Debe ingresar un número.{Style.RESET_ALL}")
                
                pause()
            
            elif option == "4":
                # Guardar y salir
                print(f"{Fore.GREEN}Cambios guardados correctamente.{Style.RESET_ALL}")
                pause()
                editing = False
                return True
            
            elif option == "0":
                # Cancelar
                return False
            
            else:
                print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")
                pause()
    
    def delete_scorecard(self, scorecard_id):
        """
        Elimina una tarjeta.
        
        Args:
            scorecard_id (int): ID de la tarjeta a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        clear_screen()
        print(format_title("ELIMINAR TARJETA"))
        
        # Confirmar eliminación
        print(f"{Fore.RED}{Style.BRIGHT}¡ATENCIÓN! Esta acción no se puede deshacer.{Style.RESET_ALL}")
        confirm = input(f"¿Está seguro de que desea eliminar la tarjeta #{scorecard_id}? (s/n): ")
        
        if confirm.lower() == 's':
            success = self.scorecard_controller.delete_scorecard(scorecard_id)
            
            if success:
                print(f"{Fore.GREEN}Tarjeta eliminada correctamente.{Style.RESET_ALL}")
                pause()
                return True
            else:
                print(f"{Fore.RED}Error al eliminar la tarjeta.{Style.RESET_ALL}")
                pause()
                return False
        else:
            print("Operación cancelada.")
            pause()
            return False
    
    def show_scorecard_options(self, scorecard):
        """
        Muestra opciones para gestionar una tarjeta.
        
        Args:
            scorecard: Tarjeta a gestionar
            
        Returns:
            bool: True si se realizó alguna acción, False en caso contrario
        """
        while True:
            clear_screen()
            print(format_title(f"OPCIONES DE TARJETA #{scorecard.id}"))
            
            # Mostrar información básica
            player = self.player_controller.get_player(scorecard.player_id)
            course = self.course_controller.get_course(scorecard.course_id)
            
            if player and course:
                print(f"\n{Fore.CYAN}Información básica:{Style.RESET_ALL}")
                print(f"  Jugador: {player.first_name} {player.surname}")
                print(f"  Campo: {course.name}")
                print(f"  Fecha: {scorecard.date}")
                print(f"  Total golpes: {scorecard.total_strokes()}")
                
                if hasattr(scorecard, 'total_points'):
                    print(f"  Total puntos: {scorecard.total_points()}")
            
            # Mostrar opciones
            print(f"\n{Fore.GREEN}Opciones disponibles:{Style.RESET_ALL}")
            print("  1. Ver detalles")
            print("  2. Editar tarjeta")
            print("  3. Eliminar tarjeta")
            print("  4. Ver estadísticas")
            print("  0. Volver")
            
            option = input("\nSeleccione una opción: ")
            
            if option == "1":
                # Ver detalles
                self.display_scorecard_details(scorecard)
            
            elif option == "2":
                # Editar tarjeta
                self.edit_scorecard(scorecard)
                # Recargar tarjeta con los nuevos datos
                scorecard = self.scorecard_controller.get_scorecard(scorecard.id)
            
            elif option == "3":
                # Eliminar tarjeta
                if self.delete_scorecard(scorecard.id):
                    return True
            
            elif option == "4":
                # Ver estadísticas
                from src.views.scorecard.scorecard_stats_view import ScorecardStatsView
                stats_view = ScorecardStatsView(
                    self.scorecard_controller,
                    self.player_controller,
                    self.course_controller
                )
                stats_view.show_scorecard_stats(scorecard.id)
            
            elif option == "0":
                # Volver
                return False
            
            else:
                print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")
                pause()
