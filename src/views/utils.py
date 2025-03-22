"""
Utilidades para las vistas de la aplicación.
"""
import os
from colorama import Fore, Style, init

# Inicializar colorama para formateo de texto en consola
init(autoreset=True)

def clear_screen():
    """
    Limpia la pantalla de la consola.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    """
    Pausa la ejecución hasta que el usuario presione Enter.
    """
    input("Presione Enter para continuar...")

def format_title(title):
    """
    Formatea un título para mostrarlo en la consola.
    
    Args:
        title (str): Título a formatear
        
    Returns:
        str: Título formateado
    """
    return f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 60}\n{title.center(60)}\n{'=' * 60}{Style.RESET_ALL}"

def format_info(text):
    """
    Formatea un texto informativo para mostrarlo en la consola.
    
    Args:
        text (str): Texto a formatear
        
    Returns:
        str: Texto formateado
    """
    return f"{Fore.GREEN}{text}{Style.RESET_ALL}"

def format_error(text):
    """
    Formatea un texto de error para mostrarlo en la consola.
    
    Args:
        text (str): Texto a formatear
        
    Returns:
        str: Texto formateado
    """
    return f"{Fore.RED}{text}{Style.RESET_ALL}"

def format_warning(text):
    """
    Formatea un texto de advertencia para mostrarlo en la consola.
    
    Args:
        text (str): Texto a formatear
        
    Returns:
        str: Texto formateado
    """
    return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"

def format_table(headers, rows, widths=None):
    """
    Formatea una tabla para mostrarla en la consola.
    
    Args:
        headers (list): Lista de encabezados de la tabla
        rows (list): Lista de filas de la tabla
        widths (list, optional): Lista de anchos para cada columna
        
    Returns:
        str: Tabla formateada
    """
    if not widths:
        # Calcular anchos automáticamente basados en el contenido
        widths = []
        for i in range(len(headers)):
            col_values = [str(row[i]) if i < len(row) else "" for row in rows]
            col_values.append(str(headers[i]))
            widths.append(max(len(val) for val in col_values) + 2)
    
    # Crear línea de separación
    separator = "+" + "+".join("-" * width for width in widths) + "+"
    
    # Formatear encabezados
    header_row = "|"
    for i, header in enumerate(headers):
        header_row += f" {Fore.CYAN}{Style.BRIGHT}{str(header).center(widths[i]-2)}{Style.RESET_ALL} |"
    
    # Formatear filas
    formatted_rows = []
    for row in rows:
        formatted_row = "|"
        for i, cell in enumerate(row):
            if i < len(widths):
                formatted_row += f" {str(cell).ljust(widths[i]-2)} |"
        formatted_rows.append(formatted_row)
    
    # Combinar todo
    table = separator + "\n" + header_row + "\n" + separator + "\n"
    table += "\n".join(formatted_rows)
    table += "\n" + separator
    
    return table
