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
    
    def __str__(self):
        return f"{self.name} ({self.location}) - Par {self.par_total}"
    
    @classmethod
    def from_db_row(cls, row):
        """Crea una instancia de Course a partir de una fila de la base de datos"""
        import json
        
        # Intentar parsear los datos como JSON
        try:
            hole_pars = json.loads(row['hole_pars']) if row['hole_pars'] else []
        except (json.JSONDecodeError, TypeError):
            # Si falla, intentar el método antiguo (separado por comas)
            hole_pars = [int(x) for x in row['hole_pars'].split(',') if x.strip()] if row['hole_pars'] else []
        
        try:
            hole_handicaps = json.loads(row['hole_handicaps']) if row['hole_handicaps'] else []
        except (json.JSONDecodeError, TypeError):
            # Si falla, intentar el método antiguo (separado por comas)
            hole_handicaps = [int(x) for x in row['hole_handicaps'].split(',') if x.strip()] if row['hole_handicaps'] else []
        
        return cls(
            id=row['id'],
            name=row['name'],
            location=row['location'],
            slope=row['slope'],
            course_rating=row['course_rating'],
            par_total=row['par_total'],
            hole_pars=hole_pars,
            hole_handicaps=hole_handicaps
        )
