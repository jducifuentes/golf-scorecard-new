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
        # Propiedad calculada para facilitar el acceso al nombre completo
        self.full_name = f"{first_name} {surname}"
    
    def __str__(self):
        return f"{self.first_name} {self.surname} (Hcp: {self.handicap})"
    
    @classmethod
    def from_db_row(cls, row):
        """
        Crea una instancia de Player a partir de una fila de la base de datos.
        
        Args:
            row (dict o tuple): Fila de la base de datos
            
        Returns:
            Player: Instancia de Player
        """
        if isinstance(row, dict):
            return cls(
                id=row.get('id'),
                first_name=row.get('first_name', ''),
                surname=row.get('surname', ''),
                handicap=row.get('handicap', 0.0)
            )
        else:
            # Si es una tupla, asumimos el orden tradicional
            return cls(
                id=row[0],
                first_name=row[1],
                surname=row[2],
                handicap=row[3]
            )
