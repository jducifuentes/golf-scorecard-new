"""
Utilidades para exportar tarjetas de puntuación a diferentes formatos.
"""
import os
import csv
import json
from datetime import datetime


class ScorecardExport:
    """
    Clase para exportar tarjetas de puntuación a diferentes formatos.
    """
    
    @staticmethod
    def export_to_csv(scorecards, player_controller=None, course_controller=None, 
                      filename=None, directory=None):
        """
        Exporta una lista de tarjetas a un archivo CSV.
        
        Args:
            scorecards (list): Lista de objetos Scorecard
            player_controller: Controlador de jugadores (opcional)
            course_controller: Controlador de campos (opcional)
            filename (str, optional): Nombre del archivo. Si no se especifica,
                                      se genera automáticamente.
            directory (str, optional): Directorio donde guardar el archivo.
                                       Por defecto es el directorio actual.
                                       
        Returns:
            tuple: (éxito, mensaje, ruta_del_archivo)
        """
        try:
            # Crear directorio de exportación si no existe
            if not directory:
                directory = os.path.join(os.getcwd(), 'exports')
            
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Generar nombre de archivo si no se especifica
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"scorecards_export_{timestamp}.csv"
            
            # Asegurar que el archivo tenga extensión .csv
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            filepath = os.path.join(directory, filename)
            
            # Preparar los datos para exportar
            export_data = []
            
            for scorecard in scorecards:
                # Obtener datos adicionales si están disponibles los controladores
                player_name = "Desconocido"
                course_name = "Desconocido"
                
                if player_controller and scorecard.player_id:
                    player = player_controller.get_player(scorecard.player_id)
                    if player:
                        player_name = f"{player.first_name} {player.surname}"
                
                if course_controller and scorecard.course_id:
                    course = course_controller.get_course(scorecard.course_id)
                    if course:
                        course_name = course.name
                
                # Datos básicos de la tarjeta
                row = {
                    'ID': scorecard.id,
                    'Fecha': scorecard.date,
                    'Jugador ID': scorecard.player_id,
                    'Jugador': player_name,
                    'Campo ID': scorecard.course_id,
                    'Campo': course_name,
                    'Handicap de Juego': scorecard.playing_handicap,
                    'Coeficiente': scorecard.handicap_coefficient,
                    'Total Golpes': scorecard.total_strokes(),
                    'Total Golpes Netos': scorecard.total_handicap_strokes(),
                    'Total Puntos': scorecard.total_points()
                }
                
                # Añadir datos por hoyo
                for i, stroke in enumerate(scorecard.strokes):
                    hole_num = i + 1
                    row[f'Hoyo {hole_num} Golpes'] = stroke
                    
                    if scorecard.handicap_strokes and i < len(scorecard.handicap_strokes):
                        row[f'Hoyo {hole_num} Neto'] = scorecard.handicap_strokes[i]
                    
                    if scorecard.points and i < len(scorecard.points):
                        row[f'Hoyo {hole_num} Puntos'] = scorecard.points[i]
                
                export_data.append(row)
            
            # Escribir al archivo CSV
            if export_data:
                # Obtener todos los campos posibles
                fieldnames = set()
                for row in export_data:
                    fieldnames.update(row.keys())
                
                # Ordenar los campos para una mejor presentación
                sorted_fields = sorted(fieldnames, key=lambda x: (
                    # Primero los campos básicos
                    0 if x in ['ID', 'Fecha', 'Jugador ID', 'Jugador', 'Campo ID', 'Campo', 
                              'Handicap de Juego', 'Coeficiente', 'Total Golpes', 
                              'Total Golpes Netos', 'Total Puntos'] else 1,
                    # Luego ordenar por número de hoyo
                    int(x.split(' ')[1]) if x.startswith('Hoyo ') and x.split(' ')[1].isdigit() else 0,
                    # Finalmente por tipo de dato (Golpes, Neto, Puntos)
                    0 if x.endswith('Golpes') else 1 if x.endswith('Neto') else 2 if x.endswith('Puntos') else 3,
                    # Alfabéticamente para el resto
                    x
                ))
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=sorted_fields)
                    writer.writeheader()
                    writer.writerows(export_data)
                
                return True, f"Exportación completada. Archivo guardado en: {filepath}", filepath
            else:
                return False, "No hay datos para exportar.", None
                
        except Exception as e:
            return False, f"Error al exportar: {str(e)}", None
    
    @staticmethod
    def export_to_json(scorecards, player_controller=None, course_controller=None, 
                       filename=None, directory=None):
        """
        Exporta una lista de tarjetas a un archivo JSON.
        
        Args:
            scorecards (list): Lista de objetos Scorecard
            player_controller: Controlador de jugadores (opcional)
            course_controller: Controlador de campos (opcional)
            filename (str, optional): Nombre del archivo. Si no se especifica,
                                      se genera automáticamente.
            directory (str, optional): Directorio donde guardar el archivo.
                                       Por defecto es el directorio actual.
                                       
        Returns:
            tuple: (éxito, mensaje, ruta_del_archivo)
        """
        try:
            # Crear directorio de exportación si no existe
            if not directory:
                directory = os.path.join(os.getcwd(), 'exports')
            
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Generar nombre de archivo si no se especifica
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"scorecards_export_{timestamp}.json"
            
            # Asegurar que el archivo tenga extensión .json
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = os.path.join(directory, filename)
            
            # Preparar los datos para exportar
            export_data = []
            
            for scorecard in scorecards:
                # Obtener datos adicionales si están disponibles los controladores
                player_data = None
                course_data = None
                
                if player_controller and scorecard.player_id:
                    player = player_controller.get_player(scorecard.player_id)
                    if player:
                        player_data = {
                            'id': player.id,
                            'first_name': player.first_name,
                            'surname': player.surname,
                            'handicap': player.handicap
                        }
                
                if course_controller and scorecard.course_id:
                    course = course_controller.get_course(scorecard.course_id)
                    if course:
                        course_data = {
                            'id': course.id,
                            'name': course.name,
                            'location': course.location,
                            'slope': course.slope,
                            'course_rating': course.course_rating,
                            'par_total': course.par_total,
                            'hole_pars': course.hole_pars,
                            'hole_handicaps': course.hole_handicaps
                        }
                
                # Datos de la tarjeta
                scorecard_data = {
                    'id': scorecard.id,
                    'date': scorecard.date,
                    'player_id': scorecard.player_id,
                    'course_id': scorecard.course_id,
                    'player': player_data,
                    'course': course_data,
                    'playing_handicap': scorecard.playing_handicap,
                    'handicap_coefficient': scorecard.handicap_coefficient,
                    'strokes': scorecard.strokes,
                    'handicap_strokes': scorecard.handicap_strokes,
                    'points': scorecard.points,
                    'totals': {
                        'strokes': scorecard.total_strokes(),
                        'handicap_strokes': scorecard.total_handicap_strokes(),
                        'points': scorecard.total_points()
                    }
                }
                
                export_data.append(scorecard_data)
            
            # Escribir al archivo JSON
            if export_data:
                with open(filepath, 'w', encoding='utf-8') as jsonfile:
                    json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
                
                return True, f"Exportación completada. Archivo guardado en: {filepath}", filepath
            else:
                return False, "No hay datos para exportar.", None
                
        except Exception as e:
            return False, f"Error al exportar: {str(e)}", None
