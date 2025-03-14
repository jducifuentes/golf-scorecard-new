from src.database import Database
from src.models.player import Player

class PlayerController:
    """
    Controlador para gestionar operaciones relacionadas con jugadores.
    """
    
    def __init__(self, database=None):
        """
        Inicializa el controlador con una conexión a la base de datos.
        
        Args:
            database (Database, optional): Instancia de la base de datos
        """
        self.db = database or Database()
    
    def add_player(self, first_name, surname, handicap):
        """
        Añade un nuevo jugador a la base de datos.
        
        Args:
            first_name (str): Nombre del jugador
            surname (str): Apellido del jugador
            handicap (float): Hándicap del jugador
            
        Returns:
            tuple: (éxito, mensaje o ID)
        """
        try:
            # Validaciones
            if not first_name or not surname:
                return False, "El nombre y apellido son obligatorios."
            
            if not isinstance(handicap, (int, float)) or handicap < -5 or handicap > 54:
                return False, "El hándicap debe ser un número entre -5 y 54."
            
            # Añadir a la base de datos
            player_id = self.db.add_player(first_name, surname, handicap)
            return True, player_id
            
        except Exception as e:
            return False, f"Error al añadir jugador: {str(e)}"
    
    def update_player(self, player_id, first_name, surname, handicap):
        """
        Actualiza los datos de un jugador existente.
        
        Args:
            player_id (int): ID del jugador
            first_name (str): Nombre del jugador
            surname (str): Apellido del jugador
            handicap (float): Hándicap del jugador
            
        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            # Validaciones
            if not first_name or not surname:
                return False, "El nombre y apellido son obligatorios."
            
            if not isinstance(handicap, (int, float)) or handicap < -5 or handicap > 54:
                return False, "El hándicap debe ser un número entre -5 y 54."
            
            # Verificar que el jugador existe
            player = self.db.get_player(player_id)
            if not player:
                return False, f"No se encontró ningún jugador con ID {player_id}."
            
            # Actualizar en la base de datos
            self.db.update_player(player_id, first_name, surname, handicap)
            return True, "Jugador actualizado correctamente."
            
        except Exception as e:
            return False, f"Error al actualizar jugador: {str(e)}"
    
    def get_player(self, player_id):
        """
        Obtiene un jugador por su ID.
        
        Args:
            player_id (int): ID del jugador
            
        Returns:
            Player: Instancia del jugador o None si no existe
        """
        try:
            player_data = self.db.get_player(player_id)
            if not player_data:
                return None
            
            return Player(
                id=player_data['id'],
                first_name=player_data['first_name'],
                surname=player_data['surname'],
                handicap=player_data['handicap']
            )
            
        except Exception:
            return None
    
    def get_players(self):
        """
        Obtiene todos los jugadores.
        
        Returns:
            list: Lista de instancias de Player
        """
        try:
            players_data = self.db.get_players()
            return [Player.from_db_row(row) for row in players_data]
            
        except Exception:
            return []
    
    def delete_player(self, player_id, delete_scorecards=False):
        """
        Elimina un jugador por su ID.
        
        Args:
            player_id (int): ID del jugador
            delete_scorecards (bool): Si es True, elimina también las tarjetas asociadas
            
        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            # Verificar que el jugador existe
            player = self.db.get_player(player_id)
            if not player:
                return False, f"No se encontró ningún jugador con ID {player_id}."
            
            # Eliminar de la base de datos
            success, message = self.db.delete_player(player_id, delete_scorecards)
            return success, message
            
        except Exception as e:
            return False, f"Error al eliminar jugador: {str(e)}"
