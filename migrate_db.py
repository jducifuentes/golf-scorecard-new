"""
Script para ejecutar las migraciones de la base de datos.
"""
import os
import sys
from colorama import init

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.db_migration import run_migrations

# Inicializar colorama
init(autoreset=True)

def main():
    """Función principal para ejecutar las migraciones"""
    try:
        # Crear directorio de datos si no existe
        os.makedirs('data', exist_ok=True)
        
        # Ruta a la base de datos
        db_path = 'data/golf.db'
        
        # Ejecutar migraciones
        success = run_migrations(db_path)
        
        if success:
            print("\nLa base de datos ha sido actualizada correctamente.")
        else:
            print("\nHubo problemas al actualizar la base de datos.")
            
    except Exception as e:
        print(f"Error durante la migración: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
