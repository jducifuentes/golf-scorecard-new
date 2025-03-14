"""
Vista principal para gestionar tarjetas de puntuación.
"""
from colorama import Fore, Style, init
from src.controllers.scorecard_controller import ScorecardController
from src.controllers.player_controller import PlayerController
from src.controllers.course_controller import CourseController
from src.utils.formatters import (
    format_title, format_subtitle, format_table, format_info, 
    format_menu_option, format_success, format_error
)
from src.utils.helpers_simple import (
    clear_screen, pause, get_input, get_number_input, 
    get_date_input, get_confirmation
)
from src.views.scorecard.scorecard_stats_view import ScorecardStatsView
from src.views.scorecard.scorecard_export import ScorecardExport
from src.views.scorecard.scorecard_utils import ScorecardUtils
import os


class ScorecardView:
    """
    Vista principal para gestionar tarjetas de puntuación.
    """
    
    def __init__(self, db):
        """
        Inicializa la vista de tarjetas.
        
        Args:
            db: Instancia de la base de datos
        """
        self.db = db
        self.scorecard_controller = ScorecardController(db)
        self.player_controller = PlayerController(db)
        self.course_controller = CourseController(db)
        self.stats_view = ScorecardStatsView(self.scorecard_controller,
                                           self.player_controller,
                                           self.course_controller)
    
    def show_menu(self):
        """Muestra el menú principal de tarjetas"""
        while True:
            clear_screen()
            print(format_title("MENÚ DE TARJETAS"))
            
            print(format_menu_option("1", "Ver todas las tarjetas"))
            print(format_menu_option("2", "Buscar tarjetas"))
            print(format_menu_option("3", "Crear nueva tarjeta"))
            print(format_menu_option("4", "Estadísticas"))
            print(format_menu_option("5", "Exportar tarjetas"))
            print(format_menu_option("0", "Volver"))
            
            option = get_number_input("\nSeleccione una opción: ")
            
            if option == 1:
                self.show_all_scorecards()
            elif option == 2:
                self.search_scorecards()
            elif option == 3:
                self.create_scorecard()
            elif option == 4:
                self.stats_view.show_menu()
            elif option == 5:
                self.export_scorecards()
            elif option == 0:
                break
            else:
                print(format_error("Opción inválida."))
                pause()
    
    def show_all_scorecards(self):
        """Muestra todas las tarjetas de puntuación"""
        clear_screen()
        print(format_title("TODAS LAS TARJETAS"))
        
        scorecards = self.scorecard_controller.get_scorecards()
        
        if not scorecards:
            print(format_info("No hay tarjetas registradas."))
            pause()
            return
        
        self._display_scorecards_list(scorecards)
    
    def search_scorecards(self):
        """Busca tarjetas según criterios"""
        clear_screen()
        print(format_title("BUSCAR TARJETAS"))
        print(format_menu_option("1", "Filtrar por jugador"))
        print(format_menu_option("2", "Filtrar por campo"))
        print(format_menu_option("3", "Filtrar por fecha"))
        print(format_menu_option("0", "Volver"))
        
        option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=3, allow_float=False)
        
        if option == 0:
            return
        
        filters = {}
        
        if option == 1:
            # Filtrar por jugador
            print(format_subtitle("Seleccionar jugador"))
            
            # Mostrar lista de jugadores
            players = self.player_controller.get_players()
            if not players:
                print(format_info("No hay jugadores registrados."))
                pause()
                return
            
            # Mostrar jugadores
            print(format_table(
                ["ID", "Nombre", "Apellido", "Hándicap"],
                [[p.id, p.first_name, p.surname, p.handicap] for p in players]
            ))
            
            player_id = get_number_input("Seleccione ID del jugador (0 para cancelar)", 
                                        default=0, min_value=0, allow_float=False)
            
            if player_id == 0:
                return
            
            filters['player_id'] = player_id
            
        elif option == 2:
            # Filtrar por campo
            print(format_subtitle("Seleccionar campo"))
            
            # Mostrar lista de campos
            courses = self.course_controller.get_courses()
            if not courses:
                print(format_info("No hay campos registrados."))
                pause()
                return
            
            # Mostrar campos
            print(format_table(
                ["ID", "Nombre", "Ubicación", "Slope", "Rating", "Par Total"],
                [[c.id, c.name, c.location, c.slope, c.course_rating, c.par_total] for c in courses]
            ))
            
            course_id = get_number_input("Seleccione ID del campo (0 para cancelar)", 
                                        default=0, min_value=0, allow_float=False)
            
            if course_id == 0:
                return
            
            filters['course_id'] = course_id
            
        elif option == 3:
            # Filtrar por fecha
            print(format_subtitle("Seleccionar rango de fechas"))
            
            start_date = get_date_input("Fecha de inicio (DD/MM/YYYY) o Enter para omitir", required=False)
            end_date = get_date_input("Fecha de fin (DD/MM/YYYY) o Enter para omitir", required=False)
            
            if start_date:
                filters['start_date'] = start_date
            if end_date:
                filters['end_date'] = end_date
        
        # Buscar tarjetas con los filtros
        scorecards = self.scorecard_controller.search_scorecards(filters)
        
        clear_screen()
        print(format_title("RESULTADOS DE BÚSQUEDA"))
        
        if not scorecards:
            print(format_info("No se encontraron tarjetas con los filtros aplicados."))
            pause()
            return
        
        self._display_scorecards_list(scorecards)
    
    def create_scorecard(self):
        """Crea una nueva tarjeta de puntuación"""
        clear_screen()
        print(format_title("CREAR NUEVA TARJETA"))
        
        # Seleccionar jugador
        print(format_subtitle("Seleccionar jugador"))
        
        # Mostrar lista de jugadores
        players = self.player_controller.get_players()
        if not players:
            print(format_info("No hay jugadores registrados. Debe crear al menos un jugador primero."))
            pause()
            return
        
        # Mostrar jugadores
        print(format_table(
            ["ID", "Nombre", "Apellido", "Hándicap"],
            [[p.id, p.first_name, p.surname, p.handicap] for p in players]
        ))
        
        player_id = get_number_input("Seleccione ID del jugador (0 para cancelar)", 
                                    default=0, min_value=0, allow_float=False)
        
        if player_id == 0:
            return
        
        # Verificar que el jugador existe
        player = next((p for p in players if p.id == player_id), None)
        if not player:
            print(format_error(f"No se encontró ningún jugador con ID {player_id}."))
            pause()
            return
        
        # Seleccionar campo
        print(format_subtitle("Seleccionar campo"))
        
        # Mostrar lista de campos
        courses = self.course_controller.get_courses()
        if not courses:
            print(format_info("No hay campos registrados. Debe crear al menos un campo primero."))
            pause()
            return
        
        # Mostrar campos
        print(format_table(
            ["ID", "Nombre", "Ubicación", "Slope", "Rating", "Par Total"],
            [[c.id, c.name, c.location, c.slope, c.course_rating, c.par_total] for c in courses]
        ))
        
        course_id = get_number_input("Seleccione ID del campo (0 para cancelar)", 
                                    default=0, min_value=0, allow_float=False)
        
        if course_id == 0:
            return
        
        # Verificar que el campo existe
        course = next((c for c in courses if c.id == course_id), None)
        if not course:
            print(format_error(f"No se encontró ningún campo con ID {course_id}."))
            pause()
            return
        
        # Obtener fecha
        date = get_date_input("Fecha de la ronda (DD/MM/YYYY) o Enter para hoy", required=False)
        
        # Obtener coeficiente de hándicap
        handicap_coefficient = get_number_input(
            "Coeficiente de hándicap (%) [100]", 
            default=100, min_value=0, max_value=100, allow_float=False
        )
        
        # Calcular hándicap de juego
        default_playing_handicap = round(player.handicap * (course.slope/113) * (handicap_coefficient/100), 1)
        
        # Permitir ajustar el hándicap de juego
        print(format_info(f"Hándicap de juego calculado: {default_playing_handicap}"))
        playing_handicap = get_number_input(
            "Hándicap de juego (Enter para usar el calculado)", 
            default=default_playing_handicap, allow_float=True
        )
        
        # Obtener golpes por hoyo
        print(format_subtitle("Introducir golpes por hoyo"))
        
        # Obtener información de los hoyos del campo
        hole_pars = course.hole_pars
        num_holes = len(hole_pars)
        
        strokes = []
        
        for i in range(num_holes):
            par = hole_pars[i]
            stroke = get_number_input(
                f"Hoyo {i+1} (Par {par})", 
                default=None, min_value=1, allow_float=False
            )
            
            if stroke is None:
                # Si el usuario no introduce un valor, terminar la entrada de golpes
                break
            
            strokes.append(stroke)
        
        # Crear la tarjeta
        success, result = self.scorecard_controller.create_scorecard(
            player_id, course_id, date, strokes, 
            playing_handicap, handicap_coefficient
        )
        
        if success:
            print(format_success("Tarjeta creada correctamente."))
            # Mostrar la tarjeta creada
            scorecard = self.scorecard_controller.get_scorecard(result)
            if scorecard:
                self._display_scorecard_details(scorecard)
        else:
            print(format_error(f"Error al crear la tarjeta: {result}"))
        
        pause()
    
    def show_statistics(self):
        """Muestra estadísticas de las tarjetas"""
        clear_screen()
        print(format_title("ESTADÍSTICAS"))
        
        # Obtener todas las tarjetas
        scorecards = self.scorecard_controller.get_scorecards()
        
        if not scorecards:
            print(format_info("No hay tarjetas registradas para mostrar estadísticas."))
            pause()
            return
        
        # Estadísticas generales
        total_scorecards = len(scorecards)
        total_strokes = sum(sc.total_strokes() for sc in scorecards)
        total_points = sum(sc.total_points() for sc in scorecards)
        
        print(format_subtitle("Estadísticas generales"))
        print(f"Total de tarjetas: {total_scorecards}")
        print(f"Total de golpes: {total_strokes}")
        print(f"Total de puntos: {total_points}")
        print(f"Media de golpes por tarjeta: {total_strokes / total_scorecards:.2f}")
        print(f"Media de puntos por tarjeta: {total_points / total_scorecards:.2f}")
        
        # Estadísticas por jugador
        print(format_subtitle("Estadísticas por jugador"))
        
        # Agrupar tarjetas por jugador
        player_stats = {}
        
        for sc in scorecards:
            if sc.player_id not in player_stats:
                player_stats[sc.player_id] = {
                    'name': sc.player_name,
                    'count': 0,
                    'total_strokes': 0,
                    'total_points': 0
                }
            
            player_stats[sc.player_id]['count'] += 1
            player_stats[sc.player_id]['total_strokes'] += sc.total_strokes()
            player_stats[sc.player_id]['total_points'] += sc.total_points()
        
        # Calcular medias y mostrar
        player_stats_list = []
        for player_id, stats in player_stats.items():
            avg_strokes = stats['total_strokes'] / stats['count']
            avg_points = stats['total_points'] / stats['count']
            
            player_stats_list.append([
                stats['name'],
                stats['count'],
                avg_strokes,
                avg_points
            ])
        
        # Ordenar por número de tarjetas (descendente)
        player_stats_list.sort(key=lambda x: x[1], reverse=True)
        
        print(format_table(
            ["Jugador", "Tarjetas", "Media Golpes", "Media Puntos"],
            [[p[0], p[1], f"{p[2]:.2f}", f"{p[3]:.2f}"] for p in player_stats_list]
        ))
        
        pause()
    
    def _display_scorecards_list(self, scorecards):
        """
        Muestra una lista de tarjetas y permite seleccionar una para ver detalles.
        
        Args:
            scorecards (list): Lista de tarjetas a mostrar
        """
        while True:
            clear_screen()
            print(format_title("LISTA DE TARJETAS"))
            
            # Preparar datos para la tabla
            table_data = []
            for i, sc in enumerate(scorecards):
                # Obtener nombres de jugador y campo si no están disponibles
                if not sc.player_name and sc.player_id:
                    player = self.player_controller.get_player(sc.player_id)
                    if player:
                        sc.player_name = f"{player.first_name} {player.surname}"
                
                if not sc.course_name and sc.course_id:
                    course = self.course_controller.get_course(sc.course_id)
                    if course:
                        sc.course_name = course.name
                
                # Formatear fecha de YYYY-MM-DD a DD/MM/YYYY para mostrar
                date_parts = sc.date.split('-') if sc.date else ['', '', '']
                display_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}" if len(date_parts) == 3 else sc.date
                
                # Calcular totales con manejo de errores
                try:
                    total_strokes = sc.total_strokes()
                except Exception:
                    total_strokes = "-"
                
                try:
                    total_points = sc.total_points()
                except Exception:
                    total_points = "-"
                
                table_data.append([
                    i + 1,  # Número en la lista
                    sc.id,
                    sc.player_name or f"ID: {sc.player_id}",
                    sc.course_name or f"ID: {sc.course_id}",
                    display_date,
                    total_strokes,
                    total_points
                ])
            
            # Mostrar tabla con formato mejorado
            headers = ["#", "ID", "Jugador", "Campo", "Fecha", "Golpes", "Puntos"]
            
            # Calcular ancho de columnas para mejor visualización
            col_widths = [max(len(str(row[i])) for row in table_data + [headers]) for i in range(len(headers))]
            
            # Imprimir encabezado
            header_row = " | ".join(f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers)))
            print(f"\n{Fore.CYAN}{Style.BRIGHT}{header_row}{Style.RESET_ALL}")
            print("-" * len(header_row))
            
            # Imprimir filas
            for row in table_data:
                formatted_row = " | ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(row)))
                print(formatted_row)
            
            print("\n" + format_menu_option("Número", "Ver detalles de la tarjeta"))
            print(format_menu_option("0", "Volver"))
            
            option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=len(scorecards), allow_float=False)
            
            if option == 0:
                return
            
            # Mostrar detalles de la tarjeta seleccionada
            selected_scorecard = scorecards[option - 1]
            self._display_scorecard_details(selected_scorecard)
    
    def _display_scorecard_details(self, scorecard):
        """
        Muestra los detalles de una tarjeta.
        
        Args:
            scorecard: Tarjeta a mostrar
        """
        clear_screen()
        print(format_title(f"DETALLES DE TARJETA #{scorecard.id}"))
        
        # Obtener información relacionada
        player = self.player_controller.get_player(scorecard.player_id)
        course = self.course_controller.get_course(scorecard.course_id)
        
        # Preparar datos usando las utilidades
        from src.views.scorecard.scorecard_utils import ScorecardUtils
        scorecard_data = ScorecardUtils.prepare_scorecard_data(
            scorecard, self.player_controller, self.course_controller, player, course
        )
        
        # Información general
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Información General:{Style.RESET_ALL}")
        print(f"  Fecha: {scorecard.date}")
        
        if player:
            print(f"  Jugador: {player.first_name} {player.surname} (Hándicap: {player.handicap})")
        else:
            print(f"  Jugador ID: {scorecard.player_id} (No encontrado)")
        
        if course:
            print(f"  Campo: {course.name} ({course.location})")
            print(f"  Par total: {course.par_total}")
            print(f"  Slope/Rating: {course.slope}/{course.course_rating}")
        else:
            print(f"  Campo ID: {scorecard.course_id} (No encontrado)")
        
        print(f"  Hándicap de juego: {scorecard.playing_handicap}")
        print(f"  Coeficiente aplicado: {scorecard.handicap_coefficient}%")
        
        # Resultados
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Resultados:{Style.RESET_ALL}")
        print(f"  Total de golpes: {scorecard_data['total_strokes']}")
        
        if 'vs_par' in scorecard_data:
            print(f"  Diferencia con el par: {scorecard_data['vs_par_text']}")
        
        print(f"  Total de golpes netos: {scorecard_data['total_handicap_strokes']}")
        
        if 'vs_handicap_par' in scorecard_data:
            print(f"  Diferencia neta con el par: {scorecard_data['vs_handicap_par_text']}")
        
        print(f"  Total de puntos Stableford: {scorecard_data['total_points']}")
        
        # Mostrar resultados por hoyo si hay un campo asociado
        if course:
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
        
        # Menú de opciones
        self._show_scorecard_options(scorecard)
    
    def _show_scorecard_options(self, scorecard):
        """
        Muestra opciones para gestionar una tarjeta.
        
        Args:
            scorecard: Tarjeta a gestionar
        """
        while True:
            clear_screen()
            print(format_title(f"OPCIONES DE TARJETA #{scorecard.id}"))
            
            print(format_menu_option("1", "Editar tarjeta"))
            print(format_menu_option("2", "Eliminar tarjeta"))
            print(format_menu_option("0", "Volver"))
            
            option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=2, allow_float=False)
            
            if option == 0:
                return
            elif option == 1:
                self._edit_scorecard(scorecard)
                # Recargar la tarjeta después de editar
                updated_scorecard = self.scorecard_controller.get_scorecard(scorecard.id)
                if updated_scorecard:
                    scorecard = updated_scorecard
                else:
                    # Si la tarjeta fue eliminada durante la edición
                    return
            elif option == 2:
                if self._delete_scorecard(scorecard.id):
                    return
    
    def _edit_scorecard(self, scorecard):
        """
        Edita una tarjeta existente.
        
        Args:
            scorecard (Scorecard): Tarjeta a editar
        """
        clear_screen()
        print(format_title(f"EDITAR TARJETA #{scorecard.id}"))
        
        # Opciones de edición
        print(format_menu_option("1", "Editar jugador"))
        print(format_menu_option("2", "Editar campo"))
        print(format_menu_option("3", "Editar fecha"))
        print(format_menu_option("4", "Editar golpes"))
        print(format_menu_option("5", "Editar hándicap"))
        print(format_menu_option("0", "Volver"))
        
        option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=5, allow_float=False)
        
        if option == 0:
            return
        
        # Variables para actualización
        player_id = None
        course_id = None
        date = None
        strokes = None
        playing_handicap = None
        handicap_coefficient = None
        
        if option == 1:
            # Editar jugador
            print(format_subtitle("Seleccionar nuevo jugador"))
            
            # Mostrar lista de jugadores
            players = self.player_controller.get_players()
            if not players:
                print(format_info("No hay jugadores registrados."))
                pause()
                return
            
            # Mostrar jugadores
            print(format_table(
                ["ID", "Nombre", "Apellido", "Hándicap"],
                [[p.id, p.first_name, p.surname, p.handicap] for p in players]
            ))
            
            player_id = get_number_input("Seleccione ID del jugador (0 para cancelar)", 
                                        default=0, min_value=0, allow_float=False)
            
            if player_id == 0:
                return
            
        elif option == 2:
            # Editar campo
            print(format_subtitle("Seleccionar nuevo campo"))
            
            # Mostrar lista de campos
            courses = self.course_controller.get_courses()
            if not courses:
                print(format_info("No hay campos registrados."))
                pause()
                return
            
            # Mostrar campos
            print(format_table(
                ["ID", "Nombre", "Ubicación", "Slope", "Rating", "Par Total"],
                [[c.id, c.name, c.location, c.slope, c.course_rating, c.par_total] for c in courses]
            ))
            
            course_id = get_number_input("Seleccione ID del campo (0 para cancelar)", 
                                        default=0, min_value=0, allow_float=False)
            
            if course_id == 0:
                return
            
        elif option == 3:
            # Editar fecha
            date = get_date_input("Nueva fecha (DD/MM/YYYY)", required=True)
            
        elif option == 4:
            # Editar golpes
            print(format_subtitle("Editar golpes por hoyo"))
            
            # Mostrar golpes actuales
            current_strokes = scorecard.strokes
            
            # Obtener información de los hoyos del campo
            course = self.course_controller.get_course(scorecard.course_id)
            if not course:
                print(format_error("No se pudo obtener la información del campo."))
                pause()
                return
            
            hole_pars = course.hole_pars
            num_holes = len(hole_pars)
            
            strokes = []
            
            for i in range(num_holes):
                par = hole_pars[i]
                current = current_strokes[i] if i < len(current_strokes) else None
                current_display = f" [{current}]" if current is not None else ""
                
                stroke = get_number_input(
                    f"Hoyo {i+1} (Par {par}){current_display}", 
                    default=current, min_value=1, allow_float=False
                )
                
                if stroke is None:
                    # Si el usuario no introduce un valor y no hay valor actual, terminar
                    if current is None:
                        break
                    # Si hay valor actual, mantenerlo
                    stroke = current
                
                strokes.append(stroke)
            
        elif option == 5:
            # Editar hándicap
            print(format_subtitle("Editar hándicap"))
            
            # Mostrar valores actuales
            print(f"Coeficiente de hándicap actual: {scorecard.handicap_coefficient}%")
            print(f"Hándicap de juego actual: {scorecard.playing_handicap}")
            
            # Editar coeficiente
            handicap_coefficient = get_number_input(
                "Nuevo coeficiente de hándicap (%) [actual]", 
                default=scorecard.handicap_coefficient, min_value=0, max_value=100, allow_float=False
            )
            
            # Editar hándicap de juego
            playing_handicap = get_number_input(
                "Nuevo hándicap de juego [actual]", 
                default=scorecard.playing_handicap, allow_float=True
            )
        
        # Actualizar la tarjeta
        success, message = self.scorecard_controller.update_scorecard(
            scorecard.id, player_id, course_id, date, 
            strokes, playing_handicap, handicap_coefficient
        )
        
        if success:
            print(format_success("Tarjeta actualizada correctamente."))
        else:
            print(format_error(f"Error al actualizar la tarjeta: {message}"))
        
        pause()
    
    def _delete_scorecard(self, scorecard_id):
        """
        Elimina una tarjeta.
        
        Args:
            scorecard_id (int): ID de la tarjeta a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        if not confirm_action("¿Está seguro de que desea eliminar esta tarjeta? Esta acción no se puede deshacer."):
            return False
        
        if self.scorecard_controller.delete_scorecard(scorecard_id):
            print(format_success("Tarjeta eliminada correctamente."))
            pause()
            return True
        else:
            print(format_error("Error al eliminar la tarjeta."))
            pause()
            return False
    
    def export_scorecards(self):
        """
        Exporta las tarjetas de puntuación a diferentes formatos.
        """
        clear_screen()
        print(format_title("EXPORTAR TARJETAS"))
        
        # Obtener las tarjetas
        scorecards = self.scorecard_controller.get_scorecards()
        
        if not scorecards:
            print(format_info("No hay tarjetas para exportar."))
            pause()
            return
        
        # Mostrar opciones de exportación
        print(format_subtitle("Opciones de exportación"))
        print(format_menu_option("1", "Exportar todas las tarjetas"))
        print(format_menu_option("2", "Exportar tarjetas filtradas"))
        print(format_menu_option("0", "Volver"))
        
        option = get_number_input("\nSeleccione una opción: ")
        
        if option == 0:
            return
        
        # Obtener las tarjetas a exportar
        export_scorecards = []
        
        if option == 1:
            export_scorecards = scorecards
        elif option == 2:
            # Aplicar filtros
            filters = {}
            
            # Filtrar por jugador
            print(format_subtitle("\nFiltrar por jugador"))
            show_player_filter = get_confirmation("¿Desea filtrar por jugador?")
            
            if show_player_filter:
                players = self.player_controller.get_players()
                if players:
                    print("\nJugadores disponibles:")
                    for player in players:
                        print(f"  {player.id}: {player.first_name} {player.surname}")
                    
                    player_id = get_number_input("\nSeleccione el ID del jugador (0 para omitir): ")
                    if player_id > 0:
                        filters['player_id'] = player_id
            
            # Filtrar por campo
            print(format_subtitle("\nFiltrar por campo"))
            show_course_filter = get_confirmation("¿Desea filtrar por campo?")
            
            if show_course_filter:
                courses = self.course_controller.get_courses()
                if courses:
                    print("\nCampos disponibles:")
                    for course in courses:
                        print(f"  {course.id}: {course.name}")
                    
                    course_id = get_number_input("\nSeleccione el ID del campo (0 para omitir): ")
                    if course_id > 0:
                        filters['course_id'] = course_id
            
            # Filtrar por fecha
            print(format_subtitle("\nFiltrar por fecha"))
            show_date_filter = get_confirmation("¿Desea filtrar por fecha?")
            
            if show_date_filter:
                start_date = get_date_input("Fecha de inicio (YYYY-MM-DD, Enter para omitir): ", required=False)
                if start_date:
                    filters['start_date'] = start_date
                
                end_date = get_date_input("Fecha de fin (YYYY-MM-DD, Enter para omitir): ", required=False)
                if end_date:
                    filters['end_date'] = end_date
            
            # Buscar tarjetas con los filtros
            export_scorecards = self.scorecard_controller.search_scorecards(filters)
        
        if not export_scorecards:
            print(format_info("\nNo se encontraron tarjetas con los filtros especificados."))
            pause()
            return
        
        # Seleccionar formato de exportación
        print(format_subtitle("\nFormato de exportación"))
        print(format_menu_option("1", "CSV (Excel, LibreOffice Calc)"))
        print(format_menu_option("2", "JSON"))
        
        format_option = get_number_input("\nSeleccione un formato: ")
        
        if format_option not in [1, 2]:
            print(format_error("Opción inválida."))
            pause()
            return
        
        # Configurar directorio de exportación
        export_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        # Exportar según el formato seleccionado
        if format_option == 1:
            # Exportar a CSV
            success, message, filepath = ScorecardExport.export_to_csv(
                export_scorecards,
                self.player_controller,
                self.course_controller,
                directory=export_dir
            )
        else:
            # Exportar a JSON
            success, message, filepath = ScorecardExport.export_to_json(
                export_scorecards,
                self.player_controller,
                self.course_controller,
                directory=export_dir
            )
        
        # Mostrar resultado
        if success:
            print(format_success(message))
            print(f"\nArchivo guardado en: {filepath}")
        else:
            print(format_error(message))
        
        pause()
