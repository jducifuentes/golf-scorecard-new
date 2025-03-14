from src.database import Database
from src.models.course import Course
import json

class CourseController:
    """
    Controlador para gestionar operaciones relacionadas con campos de golf.
    """
    
    def __init__(self, database=None):
        """
        Inicializa el controlador con una conexión a la base de datos.
        
        Args:
            database (Database, optional): Instancia de la base de datos
        """
        self.db = database or Database()
    
    def add_course(self, name, location, slope, course_rating, par_total, hole_pars, hole_handicaps):
        """
        Añade un nuevo campo a la base de datos.
        
        Args:
            name (str): Nombre del campo
            location (str): Ubicación del campo
            slope (int): Valor de slope del campo
            course_rating (float): Rating del campo
            par_total (int): Par total del campo
            hole_pars (list): Lista de pares para cada hoyo
            hole_handicaps (list): Lista de hándicaps para cada hoyo
            
        Returns:
            tuple: (éxito, mensaje o ID)
        """
        try:
            # Validaciones
            if not name or not location:
                return False, "El nombre y la ubicación son obligatorios."
            
            if not isinstance(slope, (int, float)) or slope < 55 or slope > 155:
                return False, "El slope debe ser un número entre 55 y 155."
            
            if not isinstance(course_rating, (int, float)) or course_rating < 60 or course_rating > 80:
                return False, "El course rating debe ser un número entre 60 y 80."
            
            if not isinstance(par_total, int) or par_total < 27 or par_total > 73:
                return False, "El par total debe ser un número entre 27 y 73."
            
            if len(hole_pars) != 18:
                return False, "Debe especificar el par para los 18 hoyos."
            
            if sum(hole_pars) != par_total:
                return False, f"La suma de los pares ({sum(hole_pars)}) no coincide con el par total ({par_total})."
            
            if len(hole_handicaps) != 18:
                return False, "Debe especificar el hándicap para los 18 hoyos."
            
            if sorted(hole_handicaps) != list(range(1, 19)):
                return False, "Los hándicaps de los hoyos deben ser números del 1 al 18 sin repetir."
            
            # Añadir a la base de datos
            course_id = self.db.add_course(name, location, slope, course_rating, par_total, hole_pars, hole_handicaps)
            return True, course_id
            
        except Exception as e:
            return False, f"Error al añadir campo: {str(e)}"
    
    def update_course(self, course_id, name, location, slope, course_rating, par_total, hole_pars, hole_handicaps):
        """
        Actualiza los datos de un campo existente.
        
        Args:
            course_id (int): ID del campo
            name (str): Nombre del campo
            location (str): Ubicación del campo
            slope (int): Valor de slope del campo
            course_rating (float): Rating del campo
            par_total (int): Par total del campo
            hole_pars (list): Lista de pares para cada hoyo
            hole_handicaps (list): Lista de hándicaps para cada hoyo
            
        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            # Validaciones (igual que en add_course)
            if not name or not location:
                return False, "El nombre y la ubicación son obligatorios."
            
            if not isinstance(slope, (int, float)) or slope < 55 or slope > 155:
                return False, "El slope debe ser un número entre 55 y 155."
            
            if not isinstance(course_rating, (int, float)) or course_rating < 60 or course_rating > 80:
                return False, "El course rating debe ser un número entre 60 y 80."
            
            if not isinstance(par_total, int) or par_total < 27 or par_total > 73:
                return False, "El par total debe ser un número entre 27 y 73."
            
            if len(hole_pars) != 18:
                return False, "Debe especificar el par para los 18 hoyos."
            
            if sum(hole_pars) != par_total:
                return False, f"La suma de los pares ({sum(hole_pars)}) no coincide con el par total ({par_total})."
            
            if len(hole_handicaps) != 18:
                return False, "Debe especificar el hándicap para los 18 hoyos."
            
            if sorted(hole_handicaps) != list(range(1, 19)):
                return False, "Los hándicaps de los hoyos deben ser números del 1 al 18 sin repetir."
            
            # Verificar que el campo existe
            course = self.db.get_course(course_id)
            if not course:
                return False, f"No se encontró ningún campo con ID {course_id}."
            
            # Actualizar en la base de datos
            self.db.update_course(course_id, name, location, slope, course_rating, par_total, hole_pars, hole_handicaps)
            return True, "Campo actualizado correctamente."
            
        except Exception as e:
            return False, f"Error al actualizar campo: {str(e)}"
    
    def get_course(self, course_id):
        """
        Obtiene un campo por su ID.
        
        Args:
            course_id (int): ID del campo
            
        Returns:
            Course: Instancia del campo o None si no existe
        """
        try:
            course_data = self.db.get_course(course_id)
            if not course_data:
                return None
            
            # Intentar parsear los datos como JSON
            try:
                hole_pars = json.loads(course_data['hole_pars']) if course_data['hole_pars'] else []
            except (json.JSONDecodeError, TypeError):
                # Si falla, intentar el método antiguo
                hole_pars = [int(x) for x in course_data['hole_pars'].split(',') if x.strip()] if course_data['hole_pars'] else []
            
            try:
                hole_handicaps = json.loads(course_data['hole_handicaps']) if course_data['hole_handicaps'] else []
            except (json.JSONDecodeError, TypeError):
                # Si falla, intentar el método antiguo
                hole_handicaps = [int(x) for x in course_data['hole_handicaps'].split(',') if x.strip()] if course_data['hole_handicaps'] else []
            
            return Course(
                id=course_data['id'],
                name=course_data['name'],
                location=course_data['location'],
                slope=course_data['slope'],
                course_rating=course_data['course_rating'],
                par_total=course_data['par_total'],
                hole_pars=hole_pars,
                hole_handicaps=hole_handicaps
            )
            
        except Exception as e:
            print(f"Error al obtener campo: {str(e)}")
            return None
    
    def get_courses(self):
        """
        Obtiene todos los campos.
        
        Returns:
            list: Lista de instancias de Course
        """
        try:
            courses_data = self.db.get_courses()
            result = []
            
            for row in courses_data:
                try:
                    # Intentar parsear los datos como JSON
                    try:
                        hole_pars = json.loads(row['hole_pars']) if row['hole_pars'] else []
                    except (json.JSONDecodeError, TypeError):
                        # Si falla, intentar el método antiguo
                        hole_pars = [int(x) for x in row['hole_pars'].split(',') if x.strip()] if row['hole_pars'] else []
                    
                    try:
                        hole_handicaps = json.loads(row['hole_handicaps']) if row['hole_handicaps'] else []
                    except (json.JSONDecodeError, TypeError):
                        # Si falla, intentar el método antiguo
                        hole_handicaps = [int(x) for x in row['hole_handicaps'].split(',') if x.strip()] if row['hole_handicaps'] else []
                    
                    course = Course(
                        id=row['id'],
                        name=row['name'],
                        location=row['location'],
                        slope=row['slope'],
                        course_rating=row['course_rating'],
                        par_total=row['par_total'],
                        hole_pars=hole_pars,
                        hole_handicaps=hole_handicaps
                    )
                    result.append(course)
                except Exception as e:
                    print(f"Error al procesar campo: {str(e)}")
            
            return result
        except Exception as e:
            print(f"Error al obtener campos: {str(e)}")
            return []
    
    def delete_course(self, course_id, delete_scorecards=False):
        """
        Elimina un campo por su ID.
        
        Args:
            course_id (int): ID del campo
            delete_scorecards (bool): Si es True, elimina también las tarjetas asociadas
            
        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            # Verificar que el campo existe
            course = self.db.get_course(course_id)
            if not course:
                return False, f"No se encontró ningún campo con ID {course_id}."
            
            # Eliminar de la base de datos
            success, message = self.db.delete_course(course_id, delete_scorecards)
            return success, message
            
        except Exception as e:
            return False, f"Error al eliminar campo: {str(e)}"
