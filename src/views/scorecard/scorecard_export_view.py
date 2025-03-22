"""
Vista para exportar tarjetas de puntuación a diferentes formatos.
"""
import os
import json
import csv
from colorama import Fore, Style
from src.views.base_view import BaseView
from src.views.utils import format_title, format_info, clear_screen, pause


class ScorecardExportView(BaseView):
    """
    Vista para exportar tarjetas de puntuación a diferentes formatos.
    """
    
    def __init__(self, scorecard_controller, player_controller, course_controller):
        """
        Inicializa la vista de exportación de tarjetas.
        
        Args:
            scorecard_controller: Controlador de tarjetas
            player_controller: Controlador de jugadores
            course_controller: Controlador de campos
        """
        super().__init__()
        self.scorecard_controller = scorecard_controller
        self.player_controller = player_controller
        self.course_controller = course_controller
    
    def export_to_csv(self):
        """
        Exporta las tarjetas a formato CSV.
        
        Returns:
            bool: True si se exportó correctamente, False en caso contrario
        """
        clear_screen()
        print(format_title("EXPORTAR A CSV"))
        
        # Obtener tarjetas
        scorecards = self.scorecard_controller.get_scorecards()
        
        if not scorecards:
            print(f"{Fore.YELLOW}No hay tarjetas para exportar.{Style.RESET_ALL}")
            pause()
            return False
        
        # Solicitar nombre de archivo
        filename = input("\nNombre del archivo (sin extensión): ")
        
        if not filename:
            print(f"{Fore.RED}Nombre de archivo inválido.{Style.RESET_ALL}")
            pause()
            return False
        
        # Añadir extensión
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
        
        try:
            # Crear directorio de exportación si no existe
            export_dir = os.path.join(os.getcwd(), 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            # Ruta completa del archivo
            file_path = os.path.join(export_dir, filename)
            
            # Preparar datos para exportación
            export_data = []
            
            for sc in scorecards:
                # Obtener información del jugador y campo
                player = self.player_controller.get_player(sc.player_id)
                course = self.course_controller.get_course(sc.course_id)
                
                player_name = f"{player.first_name} {player.surname}" if player else f"Jugador #{sc.player_id}"
                course_name = course.name if course else f"Campo #{sc.course_id}"
                
                # Datos básicos de la tarjeta
                row = {
                    'ID': sc.id,
                    'Fecha': sc.date,
                    'Jugador': player_name,
                    'Campo': course_name,
                    'Handicap de juego': sc.playing_handicap,
                    'Coeficiente': sc.handicap_coefficient,
                    'Total golpes': sc.total_strokes(),
                    'Total puntos': sc.total_points() if hasattr(sc, 'total_points') and callable(sc.total_points) else 'N/A'
                }
                
                # Añadir golpes por hoyo
                for i, stroke in enumerate(sc.strokes):
                    row[f'Hoyo {i+1}'] = stroke
                
                export_data.append(row)
            
            # Escribir archivo CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Determinar todos los campos posibles
                fieldnames = set()
                for row in export_data:
                    fieldnames.update(row.keys())
                
                # Ordenar los campos para mejor legibilidad
                fieldnames = sorted(fieldnames, key=lambda x: (
                    0 if x == 'ID' else
                    1 if x == 'Fecha' else
                    2 if x == 'Jugador' else
                    3 if x == 'Campo' else
                    4 if x == 'Handicap de juego' else
                    5 if x == 'Coeficiente' else
                    6 if x == 'Total golpes' else
                    7 if x == 'Total puntos' else
                    8 if x.startswith('Hoyo') else
                    9
                ))
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(export_data)
            
            print(f"{Fore.GREEN}Tarjetas exportadas correctamente a {file_path}.{Style.RESET_ALL}")
            pause()
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Error al exportar las tarjetas: {str(e)}{Style.RESET_ALL}")
            pause()
            return False
    
    def export_to_json(self):
        """
        Exporta las tarjetas a formato JSON.
        
        Returns:
            bool: True si se exportó correctamente, False en caso contrario
        """
        clear_screen()
        print(format_title("EXPORTAR A JSON"))
        
        # Obtener tarjetas
        scorecards = self.scorecard_controller.get_scorecards()
        
        if not scorecards:
            print(f"{Fore.YELLOW}No hay tarjetas para exportar.{Style.RESET_ALL}")
            pause()
            return False
        
        # Solicitar nombre de archivo
        filename = input("\nNombre del archivo (sin extensión): ")
        
        if not filename:
            print(f"{Fore.RED}Nombre de archivo inválido.{Style.RESET_ALL}")
            pause()
            return False
        
        # Añadir extensión
        if not filename.lower().endswith('.json'):
            filename += '.json'
        
        try:
            # Crear directorio de exportación si no existe
            export_dir = os.path.join(os.getcwd(), 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            # Ruta completa del archivo
            file_path = os.path.join(export_dir, filename)
            
            # Preparar datos para exportación
            export_data = []
            
            for sc in scorecards:
                # Obtener información del jugador y campo
                player = self.player_controller.get_player(sc.player_id)
                course = self.course_controller.get_course(sc.course_id)
                
                # Crear diccionario con datos de la tarjeta
                scorecard_data = {
                    'id': sc.id,
                    'date': sc.date,
                    'player': {
                        'id': sc.player_id,
                        'name': f"{player.first_name} {player.surname}" if player else "Desconocido",
                        'handicap': player.handicap if player else None
                    },
                    'course': {
                        'id': sc.course_id,
                        'name': course.name if course else "Desconocido",
                        'par_total': course.par_total if course else None
                    },
                    'playing_handicap': sc.playing_handicap,
                    'handicap_coefficient': sc.handicap_coefficient,
                    'strokes': sc.strokes,
                    'total_strokes': sc.total_strokes(),
                    'total_points': sc.total_points() if hasattr(sc, 'total_points') and callable(sc.total_points) else None
                }
                
                # Añadir datos adicionales si están disponibles
                if hasattr(sc, 'handicap_strokes') and sc.handicap_strokes:
                    scorecard_data['handicap_strokes'] = sc.handicap_strokes
                
                if hasattr(sc, 'points') and sc.points:
                    scorecard_data['points'] = sc.points
                
                export_data.append(scorecard_data)
            
            # Escribir archivo JSON
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
            
            print(f"{Fore.GREEN}Tarjetas exportadas correctamente a {file_path}.{Style.RESET_ALL}")
            pause()
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Error al exportar las tarjetas: {str(e)}{Style.RESET_ALL}")
            pause()
            return False
    
    def show_export_menu(self):
        """
        Muestra el menú de exportación de tarjetas.
        """
        while True:
            clear_screen()
            print(format_title("EXPORTAR TARJETAS"))
            
            print("\nOpciones disponibles:")
            print("  1. Exportar a CSV")
            print("  2. Exportar a JSON")
            print("  0. Volver")
            
            option = input("\nSeleccione una opción: ")
            
            if option == "1":
                self.export_to_csv()
            elif option == "2":
                self.export_to_json()
            elif option == "0":
                return
            else:
                print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")
                pause()
