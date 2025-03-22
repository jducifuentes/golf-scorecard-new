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

def format_table(headers, rows, widths=None, highlight_last_row=False):
    """
    Formatea una tabla para mostrarla en la consola.
    
    Args:
        headers (list): Lista de encabezados de la tabla
        rows (list): Lista de filas de la tabla
        widths (list, optional): Lista de anchos para cada columna
        highlight_last_row (bool, optional): Si es True, destaca la última fila
        
    Returns:
        str: Tabla formateada
    """
    if not widths:
        # Calcular anchos automáticamente basados en el contenido
        widths = []
        for i in range(len(headers)):
            col_values = [str(row[i]) if i < len(row) else "" for row in rows]
            col_values.append(str(headers[i]))
            # Ajustar el ancho para códigos ANSI
            adjusted_values = []
            for val in col_values:
                # Si tiene códigos ANSI, calcular la longitud visible
                if "\033[" in val:
                    # Eliminar todos los códigos ANSI para calcular la longitud real
                    import re
                    clean_val = re.sub(r'\033\[[0-9;]+m', '', val)
                    adjusted_values.append(clean_val)
                else:
                    adjusted_values.append(val)
            widths.append(max(len(val) for val in adjusted_values) + 4)  # Añadir más espacio
    
    # Crear línea de separación
    separator = "+" + "+".join("-" * width for width in widths) + "+"
    
    # Formatear encabezados
    header_row = "|"
    for i, header in enumerate(headers):
        header_row += f" {Fore.CYAN}{Style.BRIGHT}{str(header).center(widths[i]-2)}{Style.RESET_ALL} |"
    
    # Formatear filas
    formatted_rows = []
    for idx, row in enumerate(rows):
        is_last_row = idx == len(rows) - 1
        formatted_row = "|"
        
        for i, cell in enumerate(row):
            if i < len(widths):
                cell_str = str(cell)
                # Centrar el valor si es la última fila (totales)
                if is_last_row and highlight_last_row:
                    formatted_cell = f" {Fore.WHITE}{Style.BRIGHT}{cell_str.center(widths[i]-2)}{Style.RESET_ALL} "
                else:
                    # Mantener el formato si ya tiene colores
                    if "\033[" in cell_str:  # Tiene códigos ANSI
                        # Calcular el espacio visible (sin códigos ANSI)
                        import re
                        clean_cell = re.sub(r'\033\[[0-9;]+m', '', cell_str)
                        padding_left = (widths[i] - 2 - len(clean_cell)) // 2
                        padding_right = widths[i] - 2 - len(clean_cell) - padding_left
                        formatted_cell = f" {' ' * padding_left}{cell_str}{' ' * padding_right} "
                    else:
                        formatted_cell = f" {cell_str.center(widths[i]-2)} "
                formatted_row += formatted_cell + "|"
            else:
                formatted_row += " " * (widths[-1] - 1) + "|"
        
        formatted_rows.append(formatted_row)
    
    # Crear línea de separación para la última fila si se destaca
    last_row_separator = "+" + "+".join("=" * width for width in widths) + "+" if highlight_last_row else separator
    
    # Unir todo
    table = separator + "\n" + header_row + "\n" + separator + "\n"
    table += "\n".join(formatted_rows[:-1])  # Todas las filas excepto la última
    
    if highlight_last_row and len(formatted_rows) > 0:
        # Añadir separador antes de la última fila
        table += "\n" + separator + "\n" + formatted_rows[-1] + "\n" + last_row_separator
    else:
        # Añadir la última fila sin separador especial
        table += "\n" + formatted_rows[-1] + "\n" + separator
    
    return table
