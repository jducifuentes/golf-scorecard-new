"""
Vista para gestionar la interacción con jugadores.
"""
from src.controllers.player_controller import PlayerController
from colorama import Fore, Style
from src.utils.formatters import (
    format_title, format_subtitle, format_table, 
    format_success, format_error, format_info, format_menu_option
)
from src.utils.helpers_simple import (
    clear_screen, pause, get_input, get_number_input, get_confirmation
)
from colorama import Fore, Style

class PlayerView:
    """
    Vista para gestionar la interacción con jugadores.
    """
    
    def __init__(self, controller=None):
        """
        Inicializa la vista con un controlador.
        
        Args:
            controller (PlayerController, optional): Controlador de jugadores
        """
        self.controller = controller or PlayerController()
    
    def show_players(self):
        """Muestra la lista de jugadores"""
        clear_screen()
        print(format_title("LISTA DE JUGADORES"))
        players = self.controller.get_players()
        if not players:
            print(format_info("No hay jugadores registrados."))
            if get_confirmation("¿Desea añadir un jugador ahora?", default=True):
                self.add_player()
            return
        
        # Mostrar tabla de jugadores
        headers = ["ID", "Nombre", "Apellido", "Hándicap"]
        data = [[p.id, p.first_name, p.surname, p.handicap] for p in players]
        
        # Mostrar la tabla
        print(format_table(data, headers))
        
        # Opciones
        print(f"\n{Fore.YELLOW}Opciones:{Style.RESET_ALL}")
        print(format_menu_option("1", "Editar jugador"))
        print(format_menu_option("2", "Eliminar jugador"))
        print(format_menu_option("0", "Volver"))
        
        option = get_number_input("Seleccione una opción", default=0, min_value=0, max_value=2, allow_float=False)
        
        if option == 0:
            return
        elif option == 1:
            # Solicitar ID para editar
            player_id = get_number_input("ID del jugador a editar", allow_float=False)
            if player_id is None:
                return
            self.edit_player(player_id)
        elif option == 2:
            # Solicitar ID para eliminar
            player_id = get_number_input("ID del jugador a eliminar", allow_float=False)
            if player_id is None:
                return
            self.delete_player(player_id)
    
    def edit_player(self, player_id=None):
        """
        Edita un jugador existente.
        
        Args:
            player_id (int, optional): ID del jugador a editar
        """
        clear_screen()
        print(format_title("EDITAR JUGADOR"))
        
        # Si no se proporciona ID, mostrar lista para seleccionar
        if player_id is None:
            players = self.controller.get_players()
            if not players:
                print(format_info("No hay jugadores registrados."))
                pause()
                return
            
            # Mostrar tabla de jugadores
            headers = ["ID", "Nombre", "Apellido", "Hándicap"]
            data = [[p.id, p.first_name, p.surname, p.handicap] for p in players]
            
            # Mostrar la tabla
            print(format_table(data, headers))
            
            # Solicitar ID
            player_id = get_number_input("ID del jugador a editar", allow_float=False)
            if player_id is None:
                return
        
        # Obtener jugador
        player = self.controller.get_player(player_id)
        if not player:
            print(format_error(f"No se encontró ningún jugador con ID {player_id}."))
            pause()
            return
        
        # Mostrar datos actuales
        print(format_subtitle(f"Editando jugador: {player.first_name} {player.surname}"))
        
        # Solicitar nuevos datos
        first_name = get_input("Nombre", default=player.first_name)
        if first_name is None:
            return

        surname = get_input("Apellido", default=player.surname)
        if surname is None:
            return
        
        handicap = get_number_input("Hándicap", default=player.handicap, min_value=-5, max_value=54)
        if handicap is None:
            return
        
        # Confirmar
        print("\nNuevos datos del jugador:")
        print(f"Nombre: {first_name}")
        print(f"Apellido: {surname}")
        print(f"Hándicap: {handicap}")
        
        if not get_confirmation("¿Desea guardar los cambios?", default=True):
            print(format_info("Operación cancelada."))
            pause()
        
        # Guardar
        success, message = self.controller.update_player(player_id, first_name, surname, handicap)
        
        if success:
            print(format_success(message))
        else:
            print(format_error(message))
        
        pause()
    
    def delete_player(self, player_id=None):
        """
        Elimina un jugador existente.
        
        Args:
            player_id (int, optional): ID del jugador a eliminar
        """
        clear_screen()
        print(format_title("ELIMINAR JUGADOR"))
        
        # Si no se proporciona ID, mostrar lista para seleccionar
        if player_id is None:
            players = self.controller.get_players()
            if not players:
                print(format_info("No hay jugadores registrados."))
                pause()
                return
            
            # Mostrar tabla de jugadores
            headers = ["ID", "Nombre", "Apellido", "Hándicap"]
            data = [[p.id, p.first_name, p.surname, p.handicap] for p in players]
            
            # Mostrar la tabla
            print(format_table(data, headers))
            
            # Solicitar ID
            player_id = get_number_input("ID del jugador a eliminar", allow_float=False)
            if player_id is None:
                return
        
        # Obtener jugador
        player = self.controller.get_player(player_id)
        if not player:
            print(format_error(f"No se encontró ningún jugador con ID {player_id}."))
            pause()
            return
        
        # Confirmar
        print(format_subtitle(f"¿Está seguro de eliminar al jugador {player.first_name} {player.surname}?"))
        print(format_info("Esta acción no se puede deshacer."))
        
        if not get_confirmation("¿Eliminar jugador?", default=False):
            print(format_info("Operación cancelada."))
            pause()
            return
        
        # Intentar eliminar
        success, message = self.controller.delete_player(player_id)
        
        # Si no se puede eliminar porque tiene tarjetas asociadas, ofrecer la opción de eliminarlas también
        if not success and "tarjetas asociadas" in message:
            print(format_error(message))
            print(format_info("Para eliminar el jugador, primero debe eliminar sus tarjetas asociadas."))
            
            if get_confirmation("¿Desea eliminar también las tarjetas asociadas?", default=False):
                success, message = self.controller.delete_player(player_id, delete_scorecards=True)
            else:
                print(format_info("Operación cancelada."))
                pause()
                return
        
        if success:
            print(format_success(message))
        else:
            print(format_error(message))
        
        pause()
    
    def add_player(self):
        """Añade un nuevo jugador"""
        clear_screen()
        print(format_title("AÑADIR JUGADOR"))
        
        # Solicitar datos
        first_name = get_input("Nombre")
        if first_name is None:
            return
        
        surname = get_input("Apellido")
        if surname is None:
            return
        
        handicap = get_number_input("Hándicap", default=36.0, min_value=0.0, max_value=54.0)
        if handicap is None:
            return
        
        # Confirmar
        print("\nDatos del jugador:")
        print(f"Nombre: {first_name}")
        print(f"Apellido: {surname}")
        print(f"Hándicap: {handicap}")
        
        if not get_confirmation("¿Desea añadir este jugador?", default=True):
            print(format_info("Operación cancelada."))
            pause()
            return
        
        # Guardar
        success, result = self.controller.add_player(first_name, surname, handicap)
        
        if success:
            print(format_success(f"Jugador añadido correctamente con ID {result}."))
        else:
            print(format_error(f"Error al añadir jugador: {result}"))
        
        pause()
    
    def select_player(self):
        """
        Permite al usuario seleccionar un jugador.
        
        Returns:
            int: ID del jugador seleccionado o None si se cancela
        """
        clear_screen()
        print(format_title("SELECCIONAR JUGADOR"))
        
        # Mostrar jugadores
        players = self.controller.get_players()
        
        if not players:
            print(format_info("No hay jugadores registrados."))
            print(format_info("Debe añadir un jugador primero."))
            
            if get_confirmation("¿Desea añadir un jugador ahora?", default=True):
                self.add_player()
                return self.select_player()  # Recursión para volver a intentar
            
            return None
        
        # Preparar datos para la tabla
        headers = ["ID", "Nombre", "Apellido", "Hándicap"]
        data = [[p.id, p.first_name, p.surname, p.handicap] for p in players]
        
        # Mostrar la tabla
        print(format_table(data, headers))
        print(format_info("Ingrese 0 para añadir un nuevo jugador."))
        
        # Solicitar ID
        player_id = get_number_input("ID del jugador", allow_float=False)
        if player_id is None:
            return None
        
        # Opción para añadir nuevo jugador
        if player_id == 0:
            self.add_player()
            return self.select_player()  # Recursión para volver a intentar
        
        # Verificar que el jugador existe
        player = self.controller.get_player(player_id)
        if not player:
            print(format_error(f"No se encontró ningún jugador con ID {player_id}."))
            pause()
            return self.select_player()  # Recursión para volver a intentar
        
        return player_id
