"""
Utilidades para formatear datos y presentarlos al usuario.
"""
from datetime import datetime
from colorama import Fore, Style, init
from tabulate import tabulate

# Inicializar colorama
init(autoreset=True)

def format_date(date_str, input_format='%Y-%m-%d', output_format='%d/%m/%Y'):
    """Formatea una fecha de un formato a otro"""
    if not date_str:
        return ""
    
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_str

def format_handicap(handicap):
    """Formatea un hándicap para mostrar"""
    if handicap == int(handicap):
        return str(int(handicap))
    return f"{handicap:.1f}"

def format_table(data, headers, tablefmt="grid"):
    """Formatea datos como una tabla usando tabulate"""
    return tabulate(data, headers=headers, tablefmt=tablefmt)

def format_title(title, width=60):
    """Formatea un título con un estilo atractivo"""
    return f"\n{Fore.CYAN}{Style.BRIGHT}{title.center(width)}{Style.RESET_ALL}\n{'-' * width}"

def format_subtitle(subtitle, width=60):
    """Formatea un subtítulo con un estilo atractivo"""
    return f"\n{Fore.YELLOW}{subtitle}{Style.RESET_ALL}\n{'-' * width}"

def format_success(message):
    """Formatea un mensaje de éxito"""
    return f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}"

def format_error(message):
    """Formatea un mensaje de error"""
    return f"{Fore.RED}✗ {message}{Style.RESET_ALL}"

def format_warning(message):
    """Formatea un mensaje de advertencia"""
    return f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}"

def format_info(message):
    """Formatea un mensaje informativo"""
    return f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}"

def format_prompt(message):
    """Formatea un mensaje de solicitud de entrada"""
    return f"{Fore.CYAN}> {message}: {Style.RESET_ALL}"

def format_menu_option(key, description, selected=False):
    """Formatea una opción de menú"""
    if selected:
        return f"{Fore.BLACK}{Style.BRIGHT}{Fore.CYAN}[{key}] {description}{Style.RESET_ALL}"
    return f"{Fore.WHITE}[{key}] {description}{Style.RESET_ALL}"

def format_scorecard_header(player_name, date, course_name, handicap_coefficient):
    """Formatea la cabecera de una tarjeta de puntuación"""
    date_formatted = format_date(date)
    
    header = f"{Fore.CYAN}{Style.BRIGHT}{player_name}{Style.RESET_ALL}"
    header += f" - {date_formatted}"
    header += f" - {Fore.YELLOW}{course_name}{Style.RESET_ALL}"
    header += f" (Coef. Handicap: {handicap_coefficient})"
    
    return header

def format_scorecard_table(hole_numbers, pars, handicaps, strokes, points, handicap_strokes=None):
    """
    Formatea una tabla para mostrar una tarjeta de puntuación.
    
    Args:
        hole_numbers (list): Números de los hoyos
        pars (list): Pares de cada hoyo
        handicaps (list): Índices de hándicap de cada hoyo
        strokes (list): Golpes en cada hoyo
        points (list): Puntos stableford en cada hoyo
        handicap_strokes (list, optional): Golpes de hándicap para cada hoyo
        
    Returns:
        str: Tabla formateada
    """
    # Validar que tenemos datos
    if not hole_numbers or not pars:
        return "No hay datos suficientes para mostrar la tarjeta."
    
    # Crear tabla
    table = []
    
    # Encabezados
    headers = ["Hoyo", "Par", "Hcp", "Golpes", "Res", "Pts"]
    if handicap_strokes:
        headers.insert(3, "Extra")
    
    # Filas de datos
    for i, hole in enumerate(hole_numbers):
        if i >= len(pars):
            break
            
        row = [
            hole,
            pars[i] if i < len(pars) else "-",
            handicaps[i] if i < len(handicaps) else "-"
        ]
        
        # Añadir golpes extra si están disponibles
        if handicap_strokes and i < len(handicap_strokes):
            row.append(handicap_strokes[i])
            
        # Añadir golpes
        if i < len(strokes):
            row.append(strokes[i])
            
            # Calcular resultado respecto al par
            par = pars[i] if i < len(pars) else 0
            diff = strokes[i] - par
            result = f"{diff:+d}" if diff != 0 else "E"
            row.append(result)
        else:
            row.append("-")
            row.append("-")
            
        # Colorear los puntos stableford
        if i < len(points):
            pts = points[i]
            if pts == 0:
                row.append(f"{Fore.RED}{pts}{Style.RESET_ALL}")
            elif pts == 1:
                row.append(f"{Fore.YELLOW}{pts}{Style.RESET_ALL}")
            elif pts == 2:
                row.append(f"{Fore.GREEN}{pts}{Style.RESET_ALL}")
            elif pts == 3:
                row.append(f"{Fore.CYAN}{pts}{Style.RESET_ALL}")
            elif pts >= 4:
                row.append(f"{Fore.MAGENTA}{pts}{Style.RESET_ALL}")
            else:
                row.append(pts)
        else:
            row.append("-")
            
        table.append(row)
    
    # Si tenemos 18 hoyos, mostrar totales de primera y segunda vuelta
    if len(hole_numbers) == 18:
        # Separador
        separator = ["-"] * len(headers)
        table.append(separator)
        
        # Primera vuelta (1-9)
        first_nine = ["1-9", sum(pars[:9]) if len(pars) >= 9 else "-"]
        if handicap_strokes:
            first_nine.extend([
                sum(handicaps[:9]) if len(handicaps) >= 9 else "-",
                sum(handicap_strokes[:9]) if len(handicap_strokes) >= 9 else "-",
                sum(strokes[:9]) if len(strokes) >= 9 else "-",
                "-",  # No hay resultado total
                sum(points[:9]) if len(points) >= 9 else "-"
            ])
        else:
            first_nine.extend([
                sum(handicaps[:9]) if len(handicaps) >= 9 else "-",
                sum(strokes[:9]) if len(strokes) >= 9 else "-",
                "-",  # No hay resultado total
                sum(points[:9]) if len(points) >= 9 else "-"
            ])
        table.append(first_nine)
        
        # Segunda vuelta (10-18)
        second_nine = ["10-18", sum(pars[9:]) if len(pars) >= 18 else "-"]
        if handicap_strokes:
            second_nine.extend([
                sum(handicaps[9:]) if len(handicaps) >= 18 else "-",
                sum(handicap_strokes[9:]) if len(handicap_strokes) >= 18 else "-",
                sum(strokes[9:]) if len(strokes) >= 18 else "-",
                "-",  # No hay resultado total
                sum(points[9:]) if len(points) >= 18 else "-"
            ])
        else:
            second_nine.extend([
                sum(handicaps[9:]) if len(handicaps) >= 18 else "-",
                sum(strokes[9:]) if len(strokes) >= 18 else "-",
                "-",  # No hay resultado total
                sum(points[9:]) if len(points) >= 18 else "-"
            ])
        table.append(second_nine)
        
        # Totales
        totals = ["Total", sum(pars) if pars else "-"]
        if handicap_strokes:
            totals.extend([
                sum(handicaps) if handicaps else "-",
                sum(handicap_strokes) if handicap_strokes else "-",
                sum(strokes) if strokes else "-",
                "-",  # No hay resultado total
                sum(points) if points else "-"
            ])
        else:
            totals.extend([
                sum(handicaps) if handicaps else "-",
                sum(strokes) if strokes else "-",
                "-",  # No hay resultado total
                sum(points) if points else "-"
            ])
        table.append(totals)
    
    # Formatear tabla
    return format_table(table, headers)
