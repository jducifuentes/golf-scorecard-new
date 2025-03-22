class Course:
    """
    Modelo para representar un campo de golf.
    
    Atributos:
        id (int): Identificador único del campo
        name (str): Nombre del campo
        location (str): Ubicación del campo
        slope (int): Valor de slope del campo
        course_rating (float): Rating del campo
        par_total (int): Par total del campo
        hole_pars (list): Lista de pares para cada hoyo
        hole_handicaps (list): Lista de hándicaps para cada hoyo
    """
    
    def __init__(self, id=None, name="", location="", slope=113, course_rating=72.0, 
                 par_total=72, hole_pars=None, hole_handicaps=None):
        self.id = id
        self.name = name
        self.location = location
        self.slope = slope
        self.course_rating = course_rating
        self.par_total = par_total
        self.hole_pars = hole_pars or []
        self.hole_handicaps = hole_handicaps or []
        
        # Asegurar que los valores son del tipo correcto
        if isinstance(self.slope, str):
            try:
                self.slope = int(self.slope)
            except (ValueError, TypeError):
                self.slope = 113
                
        if isinstance(self.course_rating, str):
            try:
                self.course_rating = float(self.course_rating)
            except (ValueError, TypeError):
                self.course_rating = 72.0
                
        if isinstance(self.par_total, str):
            try:
                self.par_total = int(self.par_total)
            except (ValueError, TypeError):
                self.par_total = 72
    
    def __str__(self):
        return f"{self.name} ({self.location}) - Par {self.par_total}"
    
    @classmethod
    def from_db_row(cls, row):
        """
        Crea una instancia de Course a partir de una fila de la base de datos.
        
        Args:
            row (dict o tuple): Fila de la base de datos
            
        Returns:
            Course: Instancia de Course
        """
        import json
        
        if not row:
            return None
            
        if isinstance(row, dict):
            # Intentar parsear los datos como JSON
            try:
                hole_pars = json.loads(row.get('hole_pars', '[]')) if row.get('hole_pars') else []
            except (json.JSONDecodeError, TypeError):
                # Si falla, intentar el método antiguo (separado por comas)
                try:
                    hole_pars = [int(x) for x in row.get('hole_pars', '').split(',') if x.strip()] if row.get('hole_pars') else []
                except (ValueError, AttributeError):
                    hole_pars = []
            
            try:
                hole_handicaps = json.loads(row.get('hole_handicaps', '[]')) if row.get('hole_handicaps') else []
            except (json.JSONDecodeError, TypeError):
                # Si falla, intentar el método antiguo (separado por comas)
                try:
                    hole_handicaps = [int(x) for x in row.get('hole_handicaps', '').split(',') if x.strip()] if row.get('hole_handicaps') else []
                except (ValueError, AttributeError):
                    hole_handicaps = []
            
            return cls(
                id=row.get('id'),
                name=row.get('name', ''),
                location=row.get('location', ''),
                slope=row.get('slope', 113),
                course_rating=row.get('course_rating', 72.0),
                par_total=row.get('par_total', 72),
                hole_pars=hole_pars,
                hole_handicaps=hole_handicaps
            )
        else:
            # Si es una tupla, asumimos el orden tradicional
            try:
                # Intentar parsear los datos como JSON
                try:
                    hole_pars = json.loads(row[6]) if row[6] else []
                except (json.JSONDecodeError, TypeError, IndexError):
                    # Si falla, intentar el método antiguo (separado por comas)
                    try:
                        hole_pars = [int(x) for x in row[6].split(',') if x.strip()] if len(row) > 6 and row[6] else []
                    except (ValueError, AttributeError, IndexError):
                        hole_pars = []
                
                try:
                    hole_handicaps = json.loads(row[7]) if len(row) > 7 and row[7] else []
                except (json.JSONDecodeError, TypeError, IndexError):
                    # Si falla, intentar el método antiguo (separado por comas)
                    try:
                        hole_handicaps = [int(x) for x in row[7].split(',') if x.strip()] if len(row) > 7 and row[7] else []
                    except (ValueError, AttributeError, IndexError):
                        hole_handicaps = []
                
                return cls(
                    id=row[0] if len(row) > 0 else None,
                    name=row[1] if len(row) > 1 else '',
                    location=row[2] if len(row) > 2 else '',
                    slope=row[3] if len(row) > 3 else 113,
                    course_rating=row[4] if len(row) > 4 else 72.0,
                    par_total=row[5] if len(row) > 5 else 72,
                    hole_pars=hole_pars,
                    hole_handicaps=hole_handicaps
                )
            except Exception as e:
                print(f"Error al crear Course desde tupla: {str(e)}")
                return cls()
