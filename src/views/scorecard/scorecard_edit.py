"""
Vista para editar tarjetas de puntuación.
"""
from datetime import datetime

from src.controllers.scorecard_controller import ScorecardController
from src.controllers.player_controller import PlayerController
from src.controllers.course_controller import CourseController
from src.models.scorecard import Scorecard
from src.utils.formatters import (
    format_title, format_subtitle, format_info, format_error, format_success, format_menu_option
)
from src.utils.helpers_simple import (
    clear_screen, pause, get_number_input, get_date_input, calculate_points, calculate_handicap_strokes, 
    calculate_playing_handicap
)
from colorama import Fore, Style

class ScorecardEditView:
    """
    Vista para editar tarjetas de puntuación.
    """
    
    def __init__(self, controller=None, player_controller=None, course_controller=None):
        """
        Inicializa la vista con controladores.
        
        Args:
            controller (ScorecardController, optional): Controlador de tarjetas
            player_controller (PlayerController, optional): Controlador de jugadores
            course_controller (CourseController, optional): Controlador de campos
        """
        self.scorecard_controller = controller or ScorecardController()
        self.player_controller = player_controller or PlayerController()
        self.course_controller = course_controller or CourseController()
    
    def add_scorecard(self):
        """
        Añade una nueva tarjeta de puntuación.
        """
        clear_screen()
        print(format_title("AÑADIR TARJETA"))
        
        # Seleccionar jugador
        players = self.player_controller.get_players()
        if not players:
            print(format_error("No hay jugadores registrados. Debe crear al menos un jugador."))
            pause()
            return
        
        print(format_subtitle("Seleccione un jugador"))
        for i, player in enumerate(players, 1):
            print(format_menu_option(str(i), f"{player.first_name} {player.surname} (Hcp: {player.handicap})"))
        
        player_option = get_number_input("Seleccione un jugador", min_value=1, max_value=len(players))
        if player_option is None:
            return
        
        player = players[player_option - 1]
        print(f"Jugador seleccionado: {player.first_name} {player.surname}")
        
        # Seleccionar campo
        courses = self.course_controller.get_courses()
        if not courses:
            print(format_error("No hay campos registrados. Debe crear al menos un campo."))
            pause()
            return
        
        print(format_subtitle("Seleccione un campo"))
        for i, course in enumerate(courses, 1):
            print(format_menu_option(str(i), f"{course.name} - {course.location}"))
        
        course_option = get_number_input("Seleccione un campo", min_value=1, max_value=len(courses))
        if course_option is None:
            return
        
        course = courses[course_option - 1]
        print(f"Campo seleccionado: {course.name}")
        
        # Ingresar fecha
        print(format_subtitle("Fecha de la ronda"))
        date = get_date_input("Fecha (YYYY-MM-DD)", default=datetime.now().strftime("%Y-%m-%d"))
        if date is None:
            return
        
        # Calcular hándicap de juego
        print(format_subtitle("Hándicap de juego"))
        
        # Calcular hándicap de juego según la fórmula: (Hcp exacto * Slope / 113) + (CR - Par)
        calculated_handicap = calculate_playing_handicap(
            player.handicap, course.slope, course.course_rating, course.par
        )
        
        print(f"Hándicap exacto: {player.handicap}")
        print(f"Slope: {course.slope}")
        print(f"Course Rating: {course.course_rating}")
        print(f"Par del campo: {course.par}")
        print(f"Hándicap de juego calculado: {calculated_handicap}")
        
        # Permitir al usuario modificar el hándicap de juego
        playing_handicap = get_number_input(
            "Hándicap de juego (dejar vacío para usar el calculado)",
            default=calculated_handicap,
            allow_float=True,
            allow_empty=True
        )
        
        if playing_handicap is None and not isinstance(playing_handicap, (int, float)):
            playing_handicap = calculated_handicap
        
        # Coeficiente de hándicap (porcentaje)
        print(format_subtitle("Coeficiente de hándicap"))
        print("El coeficiente determina qué porcentaje del hándicap se aplica.")
        print("Ejemplo: 95 para aplicar el 95% del hándicap.")
        
        handicap_coefficient = get_number_input(
            "Coeficiente (%)",
            default=95,
            min_value=0,
            max_value=100
        )
        if handicap_coefficient is None:
            return
        
        # Calcular golpes extra por hoyo
        if not course.hole_pars or not course.hole_handicaps:
            course = self.course_controller.get_course(course.id)
            if not course:
                print(format_error("No se pudo obtener la información del campo."))
                pause()
                return
        
        pars = course.hole_pars
        handicaps = course.hole_handicaps
        
        # Calcular golpes de hándicap por hoyo
        playing_coefficient = playing_handicap * (handicap_coefficient / 100)
        handicap_strokes = calculate_handicap_strokes(
            playing_coefficient, 
            course.slope, 
            course.course_rating, 
            handicaps
        )
        
        # Ingresar resultados
        print(format_subtitle("Ingrese los resultados"))
        strokes = []
        points = []
        
        for i, (par, hcp) in enumerate(zip(pars, handicaps), 1):
            # Obtener los golpes extra para este hoyo
            extra_stroke = handicap_strokes[i-1] if i <= len(handicap_strokes) else 0
            
            # Solicitar golpes
            stroke = get_number_input(
                f"Hoyo {i} - Par {par} - Hcp {hcp} - Golpes extra: {extra_stroke}",
                min_value=1,
                max_value=20
            )
            if stroke is None:
                return
            
            strokes.append(stroke)
            
            # Calcular puntos
            point = calculate_points(stroke, par, extra_stroke)
            points.append(point)
            
            print(f"  Puntos: {point}")
            print()
        
        # Mostrar resumen
        print(format_subtitle("Resumen"))
        print(f"Jugador: {player.first_name} {player.surname}")
        print(f"Campo: {course.name}")
        print(f"Fecha: {date}")
        print(f"Hándicap de juego: {playing_handicap}")
        print(f"Coeficiente aplicado: {handicap_coefficient}%")
        print(f"Hándicap final: {playing_handicap * (handicap_coefficient / 100)}")
        print(f"Total golpes: {sum(strokes)}")
        print(f"Total puntos: {sum(points)}")
        
        # Confirmar
        print()
        confirm = input("¿Guardar tarjeta? (s/n): ").lower()
        if confirm != 's':
            print("Operación cancelada.")
            pause()
            return
        
        # Guardar tarjeta
        result, message = self.scorecard_controller.add_scorecard(
            player.id,
            course.id,
            date,
            strokes,
            points,
            handicap_coefficient,
            playing_handicap
        )
        
        if result:
            print(format_success("Tarjeta guardada correctamente."))
        else:
            print(format_error(f"Error al guardar la tarjeta: {message}"))
        
        pause()
    
    def modify_scorecard(self, scorecard_id):
        """
        Modifica una tarjeta existente.
        
        Args:
            scorecard_id (int): ID de la tarjeta a modificar
        """
        clear_screen()
        print(format_title("MODIFICAR TARJETA"))
        
        # Obtener la tarjeta
        scorecard = self.scorecard_controller.get_scorecard(scorecard_id)
        if not scorecard:
            print(format_error(f"No se encontró la tarjeta con ID {scorecard_id}"))
            pause()
            return
        
        # Obtener el jugador y el campo
        player = self.player_controller.get_player(scorecard.player_id)
        course = self.course_controller.get_course(scorecard.course_id)
        
        if not player or not course:
            print(format_error("Error: No se pudo obtener la información completa de la tarjeta."))
            pause()
            return
        
        # Mostrar información actual
        print(format_subtitle("Información actual"))
        print("-" * 60)
        print(f"Jugador: {player.first_name} {player.surname}")
        print(f"Campo: {course.name}")
        print(f"Fecha: {scorecard.date}")
        print(f"Hándicap de juego: {scorecard.playing_handicap}")
        print(f"Coeficiente aplicado: {scorecard.handicap_coefficient}%")
        print(f"Total golpes: {sum(scorecard.strokes) if scorecard.strokes else 0}")
        print(f"Total puntos: {sum(scorecard.points) if scorecard.points else 0}")
        
        # Menú de opciones para modificar
        print("\n¿Qué desea modificar?")
        print("-" * 60)
        print("[1] Fecha")
        print("[2] Hándicap de juego")
        print("[3] Resultados por hoyo")
        print("[0] Cancelar")
        
        option = get_number_input("> Seleccione una opción (0-3): ", 0, 3)
        
        if option == 0:
            return
            
        elif option == 1:
            # Modificar fecha
            new_date = get_date_input("Ingrese la nueva fecha (YYYY-MM-DD): ")
            scorecard.date = new_date
            
        elif option == 2:
            # Modificar hándicap de juego
            new_handicap = get_number_input("Ingrese el nuevo hándicap de juego: ", 0, 54, allow_float=True, allow_none=True)
            scorecard.playing_handicap = new_handicap
            
        elif option == 3:
            # Modificar resultados por hoyo
            print(format_subtitle("Modificar resultados"))
            print("-" * 60)
            
            # Obtener información del campo
            course = self.course_controller.get_course(scorecard.course_id)
            if not course:
                print(format_error("No se pudo obtener la información del campo."))
                pause()
                return
                
            pars = course.hole_pars
            handicaps = course.hole_handicaps
            
            # Calcular golpes de hándicap por hoyo
            playing_handicap = scorecard.playing_handicap or 0  # Si es None, usar 0
            playing_coefficient = playing_handicap * (scorecard.handicap_coefficient / 100)
            handicap_strokes = calculate_handicap_strokes(
                playing_coefficient, 
                course.slope, 
                course.course_rating, 
                handicaps
            )
            
            # Ingresar nuevos resultados
            new_strokes = []
            new_points = []
            
            for i, (par, hcp) in enumerate(zip(pars, handicaps), 1):
                # Obtener los golpes extra para este hoyo
                extra_stroke = handicap_strokes[i-1] if i <= len(handicap_strokes) else 0
                
                # Mostrar valor actual
                current_stroke = scorecard.strokes[i-1] if i <= len(scorecard.strokes) else 0
                
                # Solicitar nuevos golpes
                stroke = get_number_input(
                    f"Hoyo {i} - Par {par} - Hcp {hcp} - Golpes extra: {extra_stroke} - Actual: {current_stroke}",
                    default=current_stroke,
                    min_value=1,
                    max_value=20
                )
                if stroke is None:
                    return
                
                new_strokes.append(stroke)
                
                # Calcular puntos
                point = calculate_points(stroke, par, extra_stroke)
                new_points.append(point)
                
                print(f"  Puntos: {point}")
                print()
            
            # Actualizar listas
            scorecard.strokes = new_strokes
            scorecard.points = new_points
        
        # Mostrar resumen de cambios
        print(format_subtitle("Resumen de cambios"))
        print(f"Jugador: {player.first_name} {player.surname}")
        print(f"Campo: {course.name}")
        print(f"Fecha: {scorecard.date}")
        print(f"Hándicap de juego: {scorecard.playing_handicap}")
        print(f"Coeficiente aplicado: {scorecard.handicap_coefficient}%")
        print(f"Total golpes: {sum(scorecard.strokes) if scorecard.strokes else 0}")
        print(f"Total puntos: {sum(scorecard.points) if scorecard.points else 0}")
        
        # Confirmar
        print()
        confirm = input("¿Guardar cambios? (s/n): ").lower()
        if confirm != 's':
            print("Operación cancelada.")
            pause()
            return
        
        # Guardar cambios
        success = self.scorecard_controller.update_scorecard(
            scorecard.id,
            scorecard.player_id,
            scorecard.course_id,
            scorecard.date,
            scorecard.strokes,
            scorecard.points,
            scorecard.handicap_coefficient,
            scorecard.playing_handicap
        )
        
        if success:
            print(format_success("Tarjeta actualizada correctamente."))
        else:
            print(format_error("Error al actualizar la tarjeta."))
        
        pause()
