class Player:
    """
    Modelo para representar un jugador de golf.
    
    Atributos:
        id (int): Identificador único del jugador
        first_name (str): Nombre del jugador
        surname (str): Apellido del jugador
        handicap (float): Hándicap del jugador
    """
    
    def __init__(self, id=None, first_name="", surname="", handicap=0.0):
        self.id = id
        self.first_name = first_name
        self.surname = surname
        self.handicap = handicap
    
    def __str__(self):
        return f"{self.first_name} {self.surname} (Hcp: {self.handicap})"
    
    @classmethod
    def from_db_row(cls, row):
        """Crea una instancia de Player a partir de una fila de la base de datos"""
        return cls(
            id=row[0],
            first_name=row[1],
            surname=row[2],
            handicap=row[3]
        )
