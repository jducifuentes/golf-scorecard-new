"""
Punto de entrada principal de la aplicación.
"""
import os
import sys
from colorama import init

# Añadir el directorio src al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import Database
from src.views.menu_view_simple import MenuViewSimple

# Inicializar colorama
init(autoreset=True)

def main():
    """Función principal de la aplicación"""
    try:
        # Crear directorio de datos si no existe
        os.makedirs('data', exist_ok=True)
        
        # Inicializar la base de datos
        db = Database('data/golf.db')
        db.create_tables()
        
        # Iniciar el menú
        menu = MenuViewSimple(db)
        menu.run()
    except KeyboardInterrupt:
        print("\nSaliendo de la aplicación...")
        return

if __name__ == "__main__":
    main()
