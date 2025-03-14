from datetime import datetime
import json

class Scorecard:
    """
    Modelo para representar una tarjeta de puntuación.
    
    Attributes:
        id (int): Identificador único
        player_id (int): ID del jugador
        course_id (int): ID del campo
        date (str): Fecha en formato YYYY-MM-DD
        strokes (list): Lista de golpes por hoyo
        points (list): Lista de puntos stableford por hoyo
        handicap_coefficient (int): Coeficiente de hándicap aplicado (como porcentaje, ej: 95 para 95%)
        playing_handicap (float): Hándicap de juego final (puede ser modificado manualmente)
        player_name (str): Nombre del jugador (opcional, para visualización)
        course_name (str): Nombre del campo (opcional, para visualización)
        course_location (str): Ubicación del campo (opcional)
        course_slope (int): Pendiente del campo (opcional)
        course_rating (float): Clasificación del campo (opcional)
        course_par_total (int): Puntuación total del campo (opcional)
        course_hole_pars (list): Puntuaciones de cada hoyo del campo (opcional)
        course_hole_handicaps (list): Hándicaps de cada hoyo del campo (opcional)
    """
    
    def __init__(self, id=None, player_id=None, course_id=None, date=None, 
                 strokes=None, points=None, handicap_coefficient=100,
                 playing_handicap=None, player_name=None, course_name=None,
                 course_location=None, course_slope=None, course_rating=None,
                 course_par_total=None, course_hole_pars=None, course_hole_handicaps=None):
        """
        Inicializa una nueva instancia de Scorecard.
        
        Args:
            id (int, optional): ID de la tarjeta
            player_id (int, optional): ID del jugador
            course_id (int, optional): ID del campo
            date (str, optional): Fecha en formato YYYY-MM-DD
            strokes (list, optional): Lista de golpes por hoyo
            points (list, optional): Lista de puntos stableford por hoyo
            handicap_coefficient (int, optional): Coeficiente de hándicap aplicado
            playing_handicap (float, optional): Hándicap de juego final
            player_name (str, optional): Nombre del jugador
            course_name (str, optional): Nombre del campo
            course_location (str, optional): Ubicación del campo
            course_slope (int, optional): Pendiente del campo
            course_rating (float, optional): Clasificación del campo
            course_par_total (int, optional): Puntuación total del campo
            course_hole_pars (list, optional): Puntuaciones de cada hoyo del campo
            course_hole_handicaps (list, optional): Hándicaps de cada hoyo del campo
        """
        self.id = id
        self.player_id = player_id
        self.course_id = course_id
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.strokes = strokes or []
        self.points = points or []
        self.handicap_coefficient = handicap_coefficient
        self.playing_handicap = playing_handicap
        self.player_name = player_name
        self.course_name = course_name
        self.course_location = course_location
        self.course_slope = course_slope
        self.course_rating = course_rating
        self.course_par_total = course_par_total
        self.course_hole_pars = course_hole_pars or []
        self.course_hole_handicaps = course_hole_handicaps or []
    
    def __str__(self):
        player_info = self.player_name or f"Jugador ID: {self.player_id}"
        course_info = self.course_name or f"Campo ID: {self.course_id}"
        return f"{player_info} - {self.date} - {course_info}"
    
    def total_strokes(self):
        """Retorna el total de golpes"""
        return sum(self.strokes) if self.strokes else 0
    
    def total_points(self):
        """Retorna el total de puntos stableford"""
        return sum(self.points) if self.points else 0
    
    @classmethod
    def from_db_row(cls, row):
        """
        Crea una instancia de Scorecard a partir de una fila de la base de datos.
        
        Args:
            row (dict): Fila de la base de datos
            
        Returns:
            Scorecard: Instancia de Scorecard
        """
        if not row:
            return None
        
        # Convertir JSON a listas
        strokes = json.loads(row['strokes']) if row['strokes'] else []
        points = json.loads(row['points']) if row['points'] else []
        
        return cls(
            id=row['id'],
            player_id=row['player_id'],
            course_id=row['course_id'],
            date=row['date'],
            strokes=strokes,
            points=points,
            handicap_coefficient=row['handicap_coefficient'],
            playing_handicap=row['playing_handicap'],
            player_name=row.get('player_name'),
            course_name=row.get('course_name')
        )
    
    @classmethod
    def from_joined_row(cls, row):
        """Crea una instancia de Scorecard a partir de una fila con join de tablas"""
        # Crear la tarjeta con los campos básicos
        scorecard = cls(
            id=row['id'],
            player_id=row['player_id'],
            course_id=row['course_id'],
            date=row['date'],
            handicap_coefficient=row['handicap_coefficient'],
            playing_handicap=row['playing_handicap']
        )
        
        # Procesar los campos de listas
        if 'strokes' in row and row['strokes']:
            try:
                # Verificar si es una cadena JSON
                if row['strokes'].startswith('['):
                    scorecard.strokes = json.loads(row['strokes'])
                else:
                    # Limpiar la cadena de texto para eliminar comas múltiples
                    clean_strokes = row['strokes'].replace(',,,', ',').replace(',,', ',')
                    # Eliminar comas al inicio y al final
                    clean_strokes = clean_strokes.strip(',')
                    scorecard.strokes = [int(x) for x in clean_strokes.split(',') if x.strip()]
            except Exception as e:
                print(f"Error al procesar strokes: {str(e)}")
                scorecard.strokes = []
        
        if 'points' in row and row['points']:
            try:
                # Verificar si es una cadena JSON
                if row['points'].startswith('['):
                    scorecard.points = json.loads(row['points'])
                else:
                    # Limpiar la cadena de texto para eliminar comas múltiples
                    clean_points = row['points'].replace(',,,', ',').replace(',,', ',')
                    # Eliminar comas al inicio y al final
                    clean_points = clean_points.strip(',')
                    scorecard.points = [int(x) for x in clean_points.split(',') if x.strip()]
            except Exception as e:
                print(f"Error al procesar points: {str(e)}")
                scorecard.points = []
        
        # Añadir información adicional si está disponible
        if 'first_name' in row and 'surname' in row:
            scorecard.player_name = f"{row['first_name']} {row['surname']}"
        
        # Asignar información del campo
        if 'name' in row:
            scorecard.course_name = row['name']
            
        if 'location' in row:
            scorecard.course_location = row['location']
            
        if 'slope' in row:
            scorecard.course_slope = row['slope']
            
        if 'course_rating' in row:
            scorecard.course_rating = row['course_rating']
            
        if 'par_total' in row:
            scorecard.course_par_total = row['par_total']
            
        if 'hole_pars' in row and row['hole_pars']:
            try:
                # Verificar si es una cadena JSON
                if isinstance(row['hole_pars'], str) and row['hole_pars'].startswith('['):
                    scorecard.course_hole_pars = json.loads(row['hole_pars'])
                elif isinstance(row['hole_pars'], list):
                    scorecard.course_hole_pars = row['hole_pars']
                else:
                    # Es una cadena de texto separada por comas
                    clean_pars = row['hole_pars'].replace(',,,', ',').replace(',,', ',')
                    clean_pars = clean_pars.strip(',')
                    scorecard.course_hole_pars = [int(x) for x in clean_pars.split(',') if x.strip()]
            except Exception as e:
                print(f"Error al procesar hole_pars: {str(e)}")
                scorecard.course_hole_pars = []
                
        if 'hole_handicaps' in row and row['hole_handicaps']:
            try:
                # Verificar si es una cadena JSON
                if isinstance(row['hole_handicaps'], str) and row['hole_handicaps'].startswith('['):
                    scorecard.course_hole_handicaps = json.loads(row['hole_handicaps'])
                elif isinstance(row['hole_handicaps'], list):
                    scorecard.course_hole_handicaps = row['hole_handicaps']
                else:
                    # Es una cadena de texto separada por comas
                    clean_handicaps = row['hole_handicaps'].replace(',,,', ',').replace(',,', ',')
                    clean_handicaps = clean_handicaps.strip(',')
                    scorecard.course_hole_handicaps = [int(x) for x in clean_handicaps.split(',') if x.strip()]
            except Exception as e:
                print(f"Error al procesar hole_handicaps: {str(e)}")
                scorecard.course_hole_handicaps = []
        
        return scorecard
