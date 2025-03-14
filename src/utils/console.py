#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilidades para formatear texto en la consola.
"""

# Códigos ANSI para colores
class Colors:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Fondos
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Estilos
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

def colorize(text, color):
    """
    Colorea un texto con el color especificado.
    
    Args:
        text (str): Texto a colorear
        color (str): Código de color ANSI
        
    Returns:
        str: Texto coloreado
    """
    return f"{color}{text}{Colors.RESET}"

def yellow(text):
    """
    Colorea un texto en amarillo.
    
    Args:
        text (str): Texto a colorear
        
    Returns:
        str: Texto coloreado en amarillo
    """
    return colorize(text, Colors.YELLOW)

def green(text):
    """
    Colorea un texto en verde.
    
    Args:
        text (str): Texto a colorear
        
    Returns:
        str: Texto coloreado en verde
    """
    return colorize(text, Colors.GREEN)

def red(text):
    """
    Colorea un texto en rojo.
    
    Args:
        text (str): Texto a colorear
        
    Returns:
        str: Texto coloreado en rojo
    """
    return colorize(text, Colors.RED)

def blue(text):
    """
    Colorea un texto en azul.
    
    Args:
        text (str): Texto a colorear
        
    Returns:
        str: Texto coloreado en azul
    """
    return colorize(text, Colors.BLUE)

def bold(text):
    """
    Pone un texto en negrita.
    
    Args:
        text (str): Texto a poner en negrita
        
    Returns:
        str: Texto en negrita
    """
    return colorize(text, Colors.BOLD)
