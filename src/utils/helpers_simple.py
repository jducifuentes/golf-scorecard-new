"""
Funciones auxiliares simplificadas para la aplicación.
"""
import os
import sys
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

def clear_screen():
    """Limpia la pantalla de la terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(message="Presione Enter para continuar..."):
    """Pausa la ejecución hasta que el usuario presione Enter"""
    input(f"\n{Fore.CYAN}{message}{Style.RESET_ALL}")

def get_input(message, default=None, validator=None, completer=None):
    """
    Solicita entrada al usuario con validación básica.
    
    Args:
        message (str): Mensaje a mostrar
        default (str, optional): Valor por defecto
        validator (callable, optional): Función de validación
        completer (list, optional): No se usa en esta versión simplificada
        
    Returns:
        str: Entrada del usuario
    """
    while True:
        try:
            print(f"{Fore.CYAN}> {message}: {Style.RESET_ALL}", end="")
            if default is not None:
                print(f"[{default}] ", end="")
            
            value = input().strip()
            
            if not value and default is not None:
                return default
            
            if not value:
                continue
            
            # Validación básica si se proporciona un validador
            if validator and callable(validator):
                try:
                    validator(value)
                except Exception as e:
                    print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
                    continue
            
            return value
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operación cancelada.{Style.RESET_ALL}")
            return None

def get_number_input(message, default=None, min_value=None, max_value=None, allow_float=True, allow_empty=False):
    """
    Solicita un número al usuario con validación.
    
    Args:
        message (str): Mensaje a mostrar
        default (str, optional): Valor por defecto
        min_value (float, optional): Valor mínimo permitido
        max_value (float, optional): Valor máximo permitido
        allow_float (bool): Si se permiten números decimales
        allow_empty (bool): Si se permite dejar el campo vacío y devolver None
        
    Returns:
        float, int or None: Número ingresado por el usuario, o None si se deja vacío y allow_empty es True
    """
    range_text = ""
    if min_value is not None and max_value is not None:
        range_text = f" ({min_value}-{max_value})"
    elif min_value is not None:
        range_text = f" (min: {min_value})"
    elif max_value is not None:
        range_text = f" (max: {max_value})"
    
    while True:
        try:
            print(f"{Fore.CYAN}> {message}{range_text}: {Style.RESET_ALL}", end="")
            if default is not None:
                print(f"[{default}] ", end="")
            
            value = input().strip()
            
            if not value:
                if default is not None:
                    value = str(default)
                elif allow_empty:
                    return None
                else:
                    continue
            
            # Reemplazar coma por punto para permitir ambos formatos
            value = value.replace(',', '.')
            
            try:
                if allow_float:
                    num_value = float(value)
                    if num_value.is_integer() and not isinstance(default, float):
                        num_value = int(num_value)
                else:
                    num_value = int(value)
                
                if min_value is not None and num_value < min_value:
                    print(f"{Fore.RED}El valor debe ser mayor o igual a {min_value}.{Style.RESET_ALL}")
                    continue
                
                if max_value is not None and num_value > max_value:
                    print(f"{Fore.RED}El valor debe ser menor o igual a {max_value}.{Style.RESET_ALL}")
                    continue
                
                return num_value
            except ValueError:
                print(f"{Fore.RED}Por favor, ingrese un número válido.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operación cancelada.{Style.RESET_ALL}")
            return None

def get_date_input(message, default=None, format_str='%d/%m/%Y'):
    """
    Solicita una fecha al usuario con validación.
    
    Args:
        message (str): Mensaje a mostrar
        default (str, optional): Valor por defecto
        format_str (str): Formato de fecha esperado
        
    Returns:
        str: Fecha en formato YYYY-MM-DD (para uso interno)
    """
    if default is None:
        default = datetime.now().strftime(format_str)
    
    while True:
        print(f"{Fore.CYAN}> {message} ({format_str}): {Style.RESET_ALL}", end="")
        print(f"[{default}] ", end="")
        
        value = input().strip()
        
        if not value:
            # Convertir el valor por defecto a formato YYYY-MM-DD para uso interno
            try:
                date_obj = datetime.strptime(default, format_str)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                # Si el default ya está en formato YYYY-MM-DD
                return default
        
        try:
            # Intentar con formato dd/mm/yyyy
            try:
                date_obj = datetime.strptime(value, '%d/%m/%Y')
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                # Intentar con formato dd-mm-yyyy
                try:
                    date_obj = datetime.strptime(value, '%d-%m-%Y')
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    # Intentar con el formato especificado
                    date_obj = datetime.strptime(value, format_str)
                    return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            print(f"{Fore.RED}Por favor, ingrese una fecha válida en formato {format_str}.{Style.RESET_ALL}")

def get_date_range_input(prompt="Seleccione un rango de fechas"):
    """
    Solicita un rango de fechas al usuario.
    
    Args:
        prompt (str): Mensaje a mostrar al usuario
    
    Returns:
        tuple: (fecha_inicio, fecha_fin) en formato YYYY-MM-DD
    """
    print(f"\n{Fore.YELLOW}{prompt}{Style.RESET_ALL}")
    print("1. Último mes")
    print("2. Último año")
    print("3. Rango personalizado")
    print("4. Todas las fechas")
    
    option = get_number_input("Opción", default=4, min_value=1, max_value=4, allow_float=False)
    
    if option is None:
        return None, None
    
    today = datetime.now()
    
    if option == 1:  # Último mes
        end_date = today
        start_date = end_date - timedelta(days=30)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    elif option == 2:  # Último año
        end_date = today
        start_date = end_date - timedelta(days=365)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    elif option == 3:  # Rango personalizado
        # Usar el formato dd/mm/yyyy para la entrada del usuario
        start_date = get_date_input("Fecha de inicio", format_str='%d/%m/%Y')
        if start_date is None:
            return None, None
        
        # La fecha ya viene en formato YYYY-MM-DD desde get_date_input
        # Convertir a dd/mm/yyyy para mostrar como valor por defecto
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                start_date_display = start_date_obj.strftime('%d/%m/%Y')
            except ValueError:
                start_date_display = today.strftime('%d/%m/%Y')
        else:
            start_date_display = today.strftime('%d/%m/%Y')
        
        end_date = get_date_input("Fecha de fin", default=today.strftime('%d/%m/%Y'), format_str='%d/%m/%Y')
        if end_date is None:
            return None, None
        
        return start_date, end_date
    
    else:  # Todas las fechas
        return None, None

def get_list_input(message, separator=',', validator=None, default=None):
    """
    Solicita una lista de valores al usuario.
    
    Args:
        message (str): Mensaje a mostrar
        separator (str): Separador de valores
        validator (callable, optional): Función para validar cada valor
        default (str, optional): Valor por defecto
        
    Returns:
        list: Lista de valores
    """
    print(f"{Fore.CYAN}> {message} (separados por '{separator}'): {Style.RESET_ALL}", end="")
    if default is not None:
        print(f"[{default}] ", end="")
    
    value = input().strip()
    
    if not value and default is not None:
        value = default
    
    if not value:
        return []
    
    items = [item.strip() for item in value.split(separator)]
    
    if validator and callable(validator):
        valid_items = []
        for item in items:
            try:
                valid_item = validator(item)
                valid_items.append(valid_item)
            except ValueError as e:
                print(f"{Fore.RED}Valor inválido '{item}': {str(e)}{Style.RESET_ALL}")
                return get_list_input(message, separator, validator, default)
        return valid_items
    
    return items

def get_confirmation(message, default=False):
    """
    Solicita confirmación al usuario (s/n).
    
    Args:
        message (str): Mensaje a mostrar
        default (bool): Valor por defecto
        
    Returns:
        bool: True si el usuario confirma, False en caso contrario
    """
    default_str = "s" if default else "n"
    
    print(f"{Fore.CYAN}> {message} (s/n): {Style.RESET_ALL}", end="")
    print(f"[{default_str}] ", end="")
    
    response = input().strip().lower()
    
    if not response:
        return default
    
    return response in ('s', 'si', 'sí', 'y', 'yes')

def calculate_points(strokes, par, handicap_strokes):
    """
    Calcula los puntos para un hoyo según las reglas oficiales de Stableford.
    
    El sistema de puntuación es el siguiente:
    - Albatros o mejor (3 bajo par o mejor): 5 puntos
    - Eagle (2 bajo par): 4 puntos
    - Birdie (1 bajo par): 3 puntos
    - Par: 2 puntos
    - Bogey (1 sobre par): 1 punto
    - Doble bogey o peor (2 o más sobre par): 0 puntos
    
    Args:
        strokes (int): Golpes realizados en el hoyo
        par (int): Par del hoyo
        handicap_strokes (int): Golpes de hándicap para ese hoyo
        
    Returns:
        int: Puntos
    """
    # Si no hay golpes registrados, retornar 0 puntos
    if strokes <= 0:
        return 0
        
    # Ajustar el par según los golpes de hándicap
    adjusted_par = par + handicap_strokes
    
    # Calcular la diferencia entre los golpes y el par ajustado
    diff = strokes - adjusted_par
    
    # Asignar puntos según la diferencia
    if diff <= -3:  # Albatros o mejor
        return 5
    elif diff == -2:  # Eagle
        return 4
    elif diff == -1:  # Birdie
        return 3
    elif diff == 0:  # Par
        return 2
    elif diff == 1:  # Bogey
        return 1
    else:  # Doble bogey o peor
        return 0

def calculate_playing_handicap(exact_handicap, slope, course_rating, par):
    """
    Calcula el hándicap de juego según la fórmula oficial:
    Hándicap de juego = (Hándicap exacto * Slope / 113) + (Course Rating - Par)
    
    Args:
        exact_handicap (float): Hándicap exacto del jugador
        slope (int): Slope del campo
        course_rating (float): Course Rating del campo
        par (int): Par del campo
        
    Returns:
        float: Hándicap de juego calculado, redondeado a 1 decimal
    """
    if exact_handicap is None or slope is None or course_rating is None or par is None:
        return 0.0
    
    # Aplicar la fórmula oficial
    playing_handicap = (exact_handicap * slope / 113) + (course_rating - par)
    
    # Redondear a 1 decimal
    return round(playing_handicap, 1)

def calculate_handicap_strokes(player_handicap, course_slope, course_rating, hole_handicaps):
    """
    Calcula los golpes de hándicap para cada hoyo.
    
    Args:
        player_handicap (float): Hándicap del jugador (ya ajustado con el coeficiente)
        course_slope (int): Slope del campo
        course_rating (float): Course Rating del campo
        hole_handicaps (list): Lista de índices de hándicap para cada hoyo
        
    Returns:
        list: Lista de golpes de hándicap para cada hoyo
    """
    # Asegurarse de que tenemos todos los datos necesarios
    if player_handicap is None or not hole_handicaps:
        return [0] * 18
    
    # Redondear el hándicap de juego al entero más cercano para distribuir golpes
    playing_handicap_rounded = round(player_handicap)
    
    # Distribuir los golpes de hándicap
    handicap_strokes = [0] * 18
    
    # Asignar golpes según el índice de hándicap de cada hoyo
    for i in range(min(18, len(hole_handicaps))):
        hcp_index = hole_handicaps[i]
        
        # Asignar un golpe si el hándicap es suficiente
        if hcp_index <= playing_handicap_rounded:
            handicap_strokes[i] = 1
            
            # Asignar un segundo golpe si el hándicap es suficiente (más de 18)
            if hcp_index + 18 <= playing_handicap_rounded:
                handicap_strokes[i] = 2
                
                # Asignar un tercer golpe si el hándicap es suficiente (más de 36)
                if hcp_index + 36 <= playing_handicap_rounded:
                    handicap_strokes[i] = 3
                    
                    # Asignar un cuarto golpe si el hándicap es suficiente (más de 54)
                    if hcp_index + 54 <= playing_handicap_rounded:
                        handicap_strokes[i] = 4
    
    return handicap_strokes
