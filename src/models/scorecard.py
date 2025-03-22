"""
Modelo para representar una tarjeta de puntuación de golf.
"""
from datetime import datetime
import json


class Scorecard:
    """
    Modelo para representar una tarjeta de puntuación de golf.
    
    Attributes:
        id (int): Identificador único de la tarjeta
        player_id (int): ID del jugador
        course_id (int): ID del campo
        date (str): Fecha de la ronda en formato YYYY-MM-DD
        strokes (list): Lista de golpes por hoyo
        handicap_strokes (list): Lista de golpes con hándicap aplicado por hoyo
        points (list): Lista de puntos stableford por hoyo
        playing_handicap (float): Hándicap de juego aplicado
        handicap_coefficient (int): Coeficiente de hándicap aplicado (como porcentaje)
    """
    
    def __init__(self, id=None, player_id=None, course_id=None, date=None, 
                 strokes=None, handicap_strokes=None, points=None, 
                 playing_handicap=None, handicap_coefficient=100):
        """
        Inicializa una nueva instancia de Scorecard.
        
        Args:
            id (int, optional): ID de la tarjeta
            player_id (int, optional): ID del jugador
            course_id (int, optional): ID del campo
            date (str, optional): Fecha en formato YYYY-MM-DD
            strokes (list, optional): Lista de golpes por hoyo
            handicap_strokes (list, optional): Lista de golpes con hándicap aplicado por hoyo
            points (list, optional): Lista de puntos stableford por hoyo
            playing_handicap (float, optional): Hándicap de juego aplicado
            handicap_coefficient (int, optional): Coeficiente de hándicap aplicado (%)
        """
        self.id = id
        self.player_id = player_id
        self.course_id = course_id
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.strokes = strokes or []
        self.handicap_strokes = handicap_strokes or []
        self.points = points or []
        self.playing_handicap = playing_handicap
        self.handicap_coefficient = handicap_coefficient
        
        # Atributos calculados
        self._player_name = None
        self._course_name = None
        self._course_data = None
    
    @property
    def player_name(self):
        """Nombre del jugador (calculado)"""
        return self._player_name
    
    @player_name.setter
    def player_name(self, value):
        self._player_name = value
    
    @property
    def course_name(self):
        """Nombre del campo (calculado)"""
        return self._course_name
    
    @course_name.setter
    def course_name(self, value):
        self._course_name = value
    
    @property
    def course_data(self):
        """Datos adicionales del campo (calculado)"""
        return self._course_data
    
    @course_data.setter
    def course_data(self, value):
        self._course_data = value
    
    def __str__(self):
        """Representación en cadena de la tarjeta"""
        player = self.player_name or f"Jugador ID: {self.player_id}"
        course = self.course_name or f"Campo ID: {self.course_id}"
        return f"{player} - {self.date} - {course}"
    
    def total_strokes(self):
        """Retorna el total de golpes brutos"""
        return sum(self.strokes) if self.strokes else 0
    
    def total_handicap_strokes(self):
        """Retorna el total de golpes netos (con hándicap)"""
        return sum(self.handicap_strokes) if self.handicap_strokes else 0
    
    def total_points(self):
        """Retorna el total de puntos stableford"""
        return sum(self.points) if self.points else 0
    
    def get_hole_result(self, hole_index):
        """
        Obtiene el resultado para un hoyo específico.
        
        Args:
            hole_index (int): Índice del hoyo (0-based)
            
        Returns:
            dict: Diccionario con los datos del hoyo
        """
        if not self.course_data or not self.course_data.get('hole_pars'):
            return {
                'hole': hole_index + 1,
                'strokes': self.strokes[hole_index] if hole_index < len(self.strokes) else None,
                'handicap_strokes': self.handicap_strokes[hole_index] if hole_index < len(self.handicap_strokes) else None,
                'points': self.points[hole_index] if hole_index < len(self.points) else None,
                'par': None,
                'handicap': None
            }
        
        hole_pars = self.course_data.get('hole_pars', [])
        hole_handicaps = self.course_data.get('hole_handicaps', [])
        
        return {
            'hole': hole_index + 1,
            'strokes': self.strokes[hole_index] if hole_index < len(self.strokes) else None,
            'handicap_strokes': self.handicap_strokes[hole_index] if hole_index < len(self.handicap_strokes) else None,
            'points': self.points[hole_index] if hole_index < len(self.points) else None,
            'par': hole_pars[hole_index] if hole_index < len(hole_pars) else None,
            'handicap': hole_handicaps[hole_index] if hole_index < len(hole_handicaps) else None
        }
    
    def get_all_holes_results(self):
        """
        Obtiene los resultados para todos los hoyos.
        
        Returns:
            list: Lista de diccionarios con los datos de cada hoyo
        """
        num_holes = max(
            len(self.strokes),
            len(self.handicap_strokes),
            len(self.points),
            len(self.course_data.get('hole_pars', [])) if self.course_data else 0
        )
        
        return [self.get_hole_result(i) for i in range(num_holes)]
    
    def to_dict(self):
        """
        Convierte la tarjeta a un diccionario.
        
        Returns:
            dict: Diccionario con los datos de la tarjeta
        """
        return {
            'id': self.id,
            'player_id': self.player_id,
            'course_id': self.course_id,
            'date': self.date,
            'strokes': self.strokes,
            'handicap_strokes': self.handicap_strokes,
            'points': self.points,
            'playing_handicap': self.playing_handicap,
            'handicap_coefficient': self.handicap_coefficient,
            'player_name': self.player_name,
            'course_name': self.course_name,
            'total_strokes': self.total_strokes(),
            'total_handicap_strokes': self.total_handicap_strokes(),
            'total_points': self.total_points()
        }
    
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
        try:
            strokes = json.loads(row.get('strokes')) if row.get('strokes') else []
        except (KeyError, json.JSONDecodeError, TypeError):
            strokes = []
            
        try:
            points = json.loads(row.get('points')) if row.get('points') else []
        except (KeyError, json.JSONDecodeError, TypeError):
            points = []
        
        # Calcular los golpes con hándicap dinámicamente
        handicap_strokes = []
        
        # Si tenemos la información del campo y el hándicap de juego, calculamos los golpes con hándicap
        if row.get('hole_handicaps') and row.get('playing_handicap') is not None:
            try:
                hole_handicaps = json.loads(row.get('hole_handicaps')) if isinstance(row.get('hole_handicaps'), str) else row.get('hole_handicaps')
                playing_handicap = row.get('playing_handicap')
                
                for i, stroke in enumerate(strokes):
                    if i < len(hole_handicaps):
                        hole_handicap = hole_handicaps[i]
                        
                        # Calcular golpes extra por hándicap para este hoyo
                        extra_strokes = 0
                        if playing_handicap is not None:
                            # Distribuir el hándicap según la dificultad de los hoyos
                            if playing_handicap >= hole_handicap:
                                extra_strokes += 1
                            # Para hándicaps altos, se pueden asignar más de un golpe extra por hoyo
                            if playing_handicap >= hole_handicap + 18:
                                extra_strokes += 1
                            # Para hándicaps muy altos
                            if playing_handicap >= hole_handicap + 36:
                                extra_strokes += 1
                        
                        # Calcular golpes netos (con hándicap)
                        net_stroke = max(1, stroke - extra_strokes)
                        handicap_strokes.append(net_stroke)
                    else:
                        # Si no hay información de hándicap para este hoyo, usar el mismo valor
                        handicap_strokes.append(stroke)
            except Exception as e:
                print(f"Error al calcular handicap_strokes: {str(e)}")
                handicap_strokes = strokes.copy()
        else:
            # Si no tenemos la información necesaria, los golpes netos son iguales a los brutos
            handicap_strokes = strokes.copy()
        
        # Crear instancia
        scorecard = cls(
            id=row.get('id'),
            player_id=row.get('player_id'),
            course_id=row.get('course_id'),
            date=row.get('date'),
            strokes=strokes,
            handicap_strokes=handicap_strokes,
            points=points,
            playing_handicap=row.get('playing_handicap'),
            handicap_coefficient=row.get('handicap_coefficient', 100)
        )
        
        # Añadir información adicional si está disponible
        if row.get('first_name') and row.get('surname'):
            scorecard.player_name = f"{row.get('first_name')} {row.get('surname')}"
        
        if row.get('name'):
            scorecard.course_name = row.get('name')
        
        # Añadir datos del campo si están disponibles
        course_data = {}
        
        if row.get('location'):
            course_data['location'] = row.get('location')
            
        if row.get('slope'):
            course_data['slope'] = row.get('slope')
            
        if row.get('course_rating'):
            course_data['course_rating'] = row.get('course_rating')
            
        if row.get('par_total'):
            course_data['par_total'] = row.get('par_total')
        
        # Procesar hole_pars y hole_handicaps
        if row.get('hole_pars'):
            try:
                if isinstance(row.get('hole_pars'), str):
                    course_data['hole_pars'] = json.loads(row.get('hole_pars'))
                else:
                    course_data['hole_pars'] = row.get('hole_pars')
            except Exception as e:
                print(f"Error al procesar hole_pars: {str(e)}")
                course_data['hole_pars'] = []
                
        if row.get('hole_handicaps'):
            try:
                if isinstance(row.get('hole_handicaps'), str):
                    course_data['hole_handicaps'] = json.loads(row.get('hole_handicaps'))
                else:
                    course_data['hole_handicaps'] = row.get('hole_handicaps')
            except Exception as e:
                print(f"Error al procesar hole_handicaps: {str(e)}")
                course_data['hole_handicaps'] = []
        
        if course_data:
            scorecard.course_data = course_data
            
        return scorecard
