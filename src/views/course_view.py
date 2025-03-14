"""
Vista para gestionar la interacción con campos de golf.
"""
from src.controllers.course_controller import CourseController
from colorama import Fore, Style
from src.utils.formatters import (
    format_title, format_subtitle, format_table, 
    format_success, format_error, format_info, format_menu_option, format_warning
)
from src.utils.helpers_simple import (
    clear_screen, pause, get_input, get_number_input, 
    get_list_input, get_confirmation
)

class CourseView:
    """
    Vista para gestionar la interacción con campos de golf.
    """
    
    def __init__(self, controller=None):
        """
        Inicializa la vista con un controlador.
        
        Args:
            controller (CourseController, optional): Controlador de campos
        """
        self.controller = controller or CourseController()
    
    def show_courses(self):
        """Muestra la lista de campos"""
        clear_screen()
        print(format_title("LISTA DE CAMPOS"))
        courses = self.controller.get_courses()
        if not courses:
            print(format_info("No hay campos registrados."))
            if get_confirmation("¿Desea añadir un campo ahora?", default=True):
                self.add_course()
            return
        
        # Mostrar tabla de campos
        headers = ["ID", "Nombre", "Ubicación", "Par", "Slope", "Rating", "Hoyos"]
        data = [[c.id, c.name, c.location, c.par_total, c.slope, c.course_rating, len(c.hole_pars)] for c in courses]
        
        # Mostrar la tabla
        print(format_table(data, headers))
        
        # Opciones
        print(f"{Fore.YELLOW}Opciones:{Style.RESET_ALL}")
        print(format_menu_option("1", "Editar campo"))
        print(format_menu_option("2", "Eliminar campo"))
        print(format_menu_option("0", "Volver"))
        
        option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=2, allow_float=False)
        
        if option == 0:
            return
        elif option == 1:
            # Solicitar ID para editar
            course_id = get_number_input("ID del campo a editar", allow_float=False)
            if course_id is None:
                return
            self.edit_course(course_id)
        elif option == 2:
            # Solicitar ID para eliminar
            course_id = get_number_input("ID del campo a eliminar", allow_float=False)
            if course_id is None:
                return
            self.delete_course(course_id)
    
    def add_course(self):
        """Añade un nuevo campo"""
        clear_screen()
        print(format_title("AÑADIR CAMPO"))
        
        # Solicitar datos básicos
        name = get_input("Nombre")
        if name is None:
            return

        location = get_input("Ubicación")
        if location is None:
            return
        
        slope = get_number_input("Slope", default=113, min_value=55, max_value=155)
        if slope is None:
            return
        
        course_rating = get_number_input("Course Rating", default=72.0, min_value=60.0, max_value=80.0)
        if course_rating is None:
            return
        
        par_total = get_number_input("Par Total", default=72, min_value=27, max_value=73, allow_float=False)
        if par_total is None:
            return
        
        # Solicitar pares de cada hoyo
        print(format_subtitle("Pares de cada hoyo"))
        hole_pars = []
        
        for i in range(1, 19):
            par = get_number_input(f"Hoyo {i}", default=4, min_value=3, max_value=5, allow_float=False)
            if par is None:
                return
            hole_pars.append(par)
        
        # Verificar que la suma de pares coincide con el par total
        if sum(hole_pars) != par_total:
            print(format_error(f"La suma de los pares ({sum(hole_pars)}) no coincide con el par total ({par_total})."))
            print(format_info("Por favor, verifique los valores e intente nuevamente."))
            pause()
            return
        
        # Solicitar hándicaps de cada hoyo
        print(format_subtitle("Hándicaps de cada hoyo"))
        print(format_info("Los hándicaps deben ser números del 1 al 18 sin repetir."))
        
        hole_handicaps = []
        for i in range(1, 19):
            while True:
                handicap = get_number_input(f"Hoyo {i}", min_value=1, max_value=18, allow_float=False)
                if handicap is None:
                    return
                
                if handicap in hole_handicaps:
                    print(format_error(f"El hándicap {handicap} ya ha sido asignado a otro hoyo."))
                else:
                    hole_handicaps.append(handicap)
                    break
        
        # Confirmar
        print("\nDatos del campo:")
        print(f"Nombre: {name}")
        print(f"Ubicación: {location}")
        print(f"Slope: {slope}")
        print(f"Course Rating: {course_rating}")
        print(f"Par Total: {par_total}")
        
        if not get_confirmation("¿Desea guardar este campo?", default=True):
            print(format_info("Operación cancelada."))
            pause()
            return
        
        # Guardar
        success, result = self.controller.add_course(
            name, location, slope, course_rating, par_total, hole_pars, hole_handicaps
        )
        
        if success:
            print(format_success(f"Campo añadido correctamente con ID {result}."))
        else:
            print(format_error(f"Error al añadir campo: {result}"))
        
        pause()
    
    def edit_course(self, course_id=None):
        """
        Edita un campo existente.
        
        Args:
            course_id (int, optional): ID del campo a editar
        """
        clear_screen()
        print(format_title("EDITAR CAMPO"))
        
        # Si no se proporciona ID, solicitar al usuario
        if course_id is None:
            course_id = self.select_course()
            if course_id is None:
                return
        
        # Obtener campo
        course = self.controller.get_course(course_id)
        if not course:
            print(format_error(f"No se encontró ningún campo con ID {course_id}."))
            pause()
            return
        
        # Mostrar datos actuales
        print(format_subtitle(f"Editando campo: {course.name}"))
        
        # Solicitar nuevos datos
        name = get_input("Nombre", default=course.name)
        if name is None:
            return

        location = get_input("Ubicación", default=course.location)
        if location is None:
            return
        
        slope = get_number_input("Slope", default=course.slope, min_value=55, max_value=155)
        if slope is None:
            return
        
        course_rating = get_number_input("Course Rating", default=course.course_rating, min_value=60.0, max_value=80.0)
        if course_rating is None:
            return
        
        par_total = get_number_input("Par Total", default=course.par_total, min_value=27, max_value=73, allow_float=False)
        if par_total is None:
            return
        
        # Solicitar pares de cada hoyo
        print(format_subtitle("Pares de cada hoyo"))
        hole_pars = []
        
        for i in range(1, 19):
            default_par = course.hole_pars[i-1] if i <= len(course.hole_pars) else 4
            par = get_number_input(f"Hoyo {i}", default=default_par, min_value=3, max_value=5, allow_float=False)
            if par is None:
                return
            hole_pars.append(par)
        
        # Verificar que la suma de pares coincide con el par total
        if sum(hole_pars) != par_total:
            print(format_error(f"La suma de los pares ({sum(hole_pars)}) no coincide con el par total ({par_total})."))
            print(format_info("Por favor, verifique los valores e intente nuevamente."))
            pause()
            return
        
        # Solicitar hándicaps de cada hoyo
        print(format_subtitle("Hándicaps de cada hoyo"))
        print(format_info("Los hándicaps deben ser números del 1 al 18 sin repetir."))
        
        # Crear una copia de los hándicaps actuales para usar como valores por defecto
        default_handicaps = course.hole_handicaps.copy() if hasattr(course, 'hole_handicaps') and course.hole_handicaps else [None] * 18
        
        hole_handicaps = []
        for i in range(1, 19):
            # Obtener el valor por defecto para este hoyo
            default_handicap = default_handicaps[i-1] if i <= len(default_handicaps) else None
            
            while True:
                # Mostrar el valor actual para este hoyo
                current_value = f" [Actual: {default_handicap}]" if default_handicap is not None else ""
                handicap = get_number_input(f"Hoyo {i}{current_value}", default=default_handicap, min_value=1, max_value=18, allow_float=False)
                
                if handicap is None:
                    return
                
                # Verificar si este hándicap ya ha sido asignado a otro hoyo en esta sesión de edición
                if handicap in hole_handicaps:
                    print(format_error(f"El hándicap {handicap} ya ha sido asignado a otro hoyo."))
                else:
                    hole_handicaps.append(handicap)
                    break
        
        # Confirmar
        print("\nNuevos datos del campo:")
        print(f"Nombre: {name}")
        print(f"Ubicación: {location}")
        print(f"Slope: {slope}")
        print(f"Course Rating: {course_rating}")
        print(f"Par Total: {par_total}")
        
        if not get_confirmation("¿Desea guardar los cambios?", default=True):
            print(format_info("Operación cancelada."))
            pause()
            return
        
        # Guardar
        success, message = self.controller.update_course(
            course_id, name, location, slope, course_rating, par_total, hole_pars, hole_handicaps
        )
        
        if success:
            print(format_success(message))
        else:
            print(format_error(message))
        
        pause()
    
    def delete_course(self, course_id=None):
        """
        Elimina un campo existente.
        
        Args:
            course_id (int, optional): ID del campo a eliminar
        """
        self._delete_course(course_id)
    
    def _delete_course(self, course_id=None):
        """
        Elimina un campo existente.
        
        Args:
            course_id (int, optional): ID del campo a eliminar
        """
        clear_screen()
        print(format_title("ELIMINAR CAMPO"))
        
        # Si no se proporciona ID, mostrar lista para seleccionar
        if course_id is None:
            courses = self.controller.get_courses()
            if not courses:
                print(format_info("No hay campos registrados."))
                pause()
                return
            
            # Mostrar tabla de campos
            headers = ["ID", "Nombre", "Par", "Hoyos"]
            data = [[c.id, c.name, c.par_total, len(c.hole_pars)] for c in courses]
            
            # Mostrar la tabla
            print(format_table(data, headers))
            
            # Solicitar ID
            course_id = get_number_input("ID del campo a eliminar", allow_float=False)
            if course_id is None:
                return
        
        # Obtener campo
        course = self.controller.get_course(course_id)
        if not course:
            print(format_error(f"No se encontró ningún campo con ID {course_id}."))
            pause()
            return
        
        # Confirmar
        print(format_subtitle(f"¿Está seguro de eliminar el campo {course.name}?"))
        print(format_warning("Esta acción no se puede deshacer."))
        
        if not get_confirmation("¿Eliminar campo?", default=False):
            print(format_info("Operación cancelada."))
            pause()
            return
        
        # Intentar eliminar
        success, message = self.controller.delete_course(course_id)
        
        # Si no se puede eliminar porque tiene tarjetas asociadas, ofrecer la opción de eliminarlas también
        if not success and "tarjetas asociadas" in message:
            print(format_error(message))
            print(format_info("Para eliminar el campo, primero debe eliminar sus tarjetas asociadas."))
            
            if get_confirmation("¿Desea eliminar también las tarjetas asociadas?", default=False):
                success, message = self.controller.delete_course(course_id, delete_scorecards=True)
            else:
                print(format_info("Operación cancelada."))
                pause()
                return
        
        if success:
            print(format_success(message))
        else:
            print(format_error(message))
        
        pause()
    
    def select_course(self):
        """
        Permite al usuario seleccionar un campo.
        
        Returns:
            int: ID del campo seleccionado o None si se cancela
        """
        clear_screen()
        print(format_title("SELECCIONAR CAMPO"))
        
        # Mostrar campos
        courses = self.controller.get_courses()
        
        if not courses:
            print(format_info("No hay campos registrados."))
            print(format_info("Debe añadir un campo primero."))
            
            if get_confirmation("¿Desea añadir un campo ahora?", default=True):
                self.add_course()
                return self.select_course()  # Recursión para volver a intentar
            
            return None
        
        # Preparar datos para la tabla
        headers = ["ID", "Nombre", "Ubicación", "Slope", "Course Rating", "Par Total"]
        data = [
            [c.id, c.name, c.location, c.slope, c.course_rating, c.par_total] 
            for c in courses
        ]
        
        # Mostrar la tabla
        print(format_table(data, headers))
        print(format_info("Ingrese 0 para añadir un nuevo campo."))
        
        # Solicitar ID
        course_id = get_number_input("ID del campo", allow_float=False)
        if course_id is None:
            return None
        
        # Opción para añadir nuevo campo
        if course_id == 0:
            self.add_course()
            return self.select_course()  # Recursión para volver a intentar
        
        # Verificar que el campo existe
        course = self.controller.get_course(course_id)
        if not course:
            print(format_error(f"No se encontró ningún campo con ID {course_id}."))
            pause()
            return self.select_course()  # Recursión para volver a intentar
        
        return course_id
