import os
import sys
import random
import json
from datetime import datetime, timedelta

# Añadir el directorio src al path para poder importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import Database
from models.player import Player
from models.course import Course
from models.scorecard import Scorecard

def add_test_data():
    """Añade datos de prueba a la base de datos."""
    # Usar la misma base de datos que la aplicación principal
    db = Database('data/golf.db')
    
    # Crear jugadores
    players = [
        {"first_name": "Juan", "surname": "García", "handicap": 12.4},
        {"first_name": "María", "surname": "López", "handicap": 18.7},
        {"first_name": "Carlos", "surname": "Martínez", "handicap": 5.2},
        {"first_name": "Ana", "surname": "Rodríguez", "handicap": 24.1}
    ]
    
    player_ids = []
    for player in players:
        player_id = db.add_player(player["first_name"], player["surname"], player["handicap"])
        player_ids.append(player_id)
        print(f"Añadido jugador: {player['first_name']} {player['surname']} (ID: {player_id})")
    
    # Crear campos
    courses = [
        {
            "name": "Club de Golf Las Encinas", 
            "location": "Madrid", 
            "pars": [4, 3, 5, 4, 4, 5, 3, 4, 4, 4, 3, 5, 4, 4, 3, 5, 4, 4],
            "handicaps": [7, 15, 1, 11, 5, 3, 17, 13, 9, 8, 16, 2, 12, 6, 18, 4, 10, 14],
            "slope": 128, 
            "course_rating": 71.2
        },
        {
            "name": "Real Club de Golf", 
            "location": "Sevilla", 
            "pars": [4, 4, 3, 5, 4, 3, 4, 5, 4, 4, 3, 5, 4, 4, 3, 5, 4, 4],
            "handicaps": [6, 12, 16, 2, 8, 18, 10, 4, 14, 5, 17, 1, 9, 11, 15, 3, 7, 13],
            "slope": 132, 
            "course_rating": 72.8
        },
        {
            "name": "Golf Costa Brava", 
            "location": "Girona", 
            "pars": [5, 4, 3, 4, 4, 5, 3, 4, 4, 4, 3, 5, 4, 4, 5, 3, 4, 4],
            "handicaps": [3, 9, 15, 7, 11, 1, 17, 13, 5, 4, 16, 2, 10, 8, 6, 18, 12, 14],
            "slope": 124, 
            "course_rating": 70.5
        }
    ]
    
    course_ids = []
    for course in courses:
        # Calcular par total
        par_total = sum(course["pars"])
        
        course_id = db.add_course(
            course["name"], 
            course["location"], 
            course["slope"], 
            course["course_rating"], 
            par_total, 
            course["pars"],  
            course["handicaps"]  
        )
        course_ids.append(course_id)
        print(f"Añadido campo: {course['name']} (ID: {course_id})")
    
    # Generar fechas aleatorias en 2024
    def random_date_in_2024():
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        return start_date + timedelta(days=random_number_of_days)
    
    # Crear tarjetas para cada jugador
    for player_id in player_ids:
        # Obtener el jugador para conocer su hándicap
        player_data = db.get_player(player_id)
        
        # Crear 3 tarjetas para cada jugador
        for i in range(3):
            # Seleccionar un campo aleatorio
            course_id = random.choice(course_ids)
            course_data = db.get_course(course_id)
            
            # Obtener pars y handicaps como listas
            try:
                # Intentar parsear como JSON
                pars = json.loads(course_data['hole_pars']) if isinstance(course_data['hole_pars'], str) else course_data['hole_pars']
                handicaps = json.loads(course_data['hole_handicaps']) if isinstance(course_data['hole_handicaps'], str) else course_data['hole_handicaps']
            except (json.JSONDecodeError, TypeError):
                # Si falla, intentar el método antiguo
                pars = [int(x) for x in course_data['hole_pars'].split(',') if x.strip()]
                handicaps = [int(x) for x in course_data['hole_handicaps'].split(',') if x.strip()]
            
            # Asegurarse de que todos los valores son enteros
            pars = [int(x) if isinstance(x, str) else x for x in pars[:18]]
            handicaps = [int(x) if isinstance(x, str) else x for x in handicaps[:18]]
            
            # Si no tenemos suficientes valores, usar valores predeterminados
            if len(pars) < 18:
                pars = [4] * 18  # Par 4 es común
            if len(handicaps) < 18:
                handicaps = list(range(1, 19))  # Handicaps del 1 al 18
            
            # Generar fecha aleatoria
            date = random_date_in_2024().strftime("%Y-%m-%d")
            
            # Generar coeficiente de hándicap: 90%, 95% o 100%
            handicap_coefficients = [90, 95, 100]
            handicap_coefficient_percent = random.choice(handicap_coefficients)
            
            # Calcular hándicap de juego
            base_handicap = round((player_data['handicap'] * course_data['slope']) / 113, 1)
            playing_handicap = round(base_handicap * (handicap_coefficient_percent / 100))
            
            # Generar golpes aleatorios para cada hoyo
            strokes = []
            points = []
            stableford = []
            
            for hole_index, par in enumerate(pars):
                # Calcular hándicap extra para este hoyo
                handicap_position = handicaps[hole_index]
                # Asegurarse de que handicap_position es un entero
                if isinstance(handicap_position, str):
                    handicap_position = int(handicap_position)
                
                extra_strokes = 0
                
                if handicap_position <= playing_handicap % 18:
                    extra_strokes = playing_handicap // 18 + 1
                else:
                    extra_strokes = playing_handicap // 18
                
                # Generar golpes aleatorios basados en el par y el hándicap
                # Jugadores mejores (hándicap bajo) tienen más probabilidad de hacer buenos golpes
                skill_factor = 1.0 - (player_data['handicap'] / 36.0)  # Factor de habilidad entre 0.33 y 0.86
                
                # Probabilidad de hacer par o mejor
                par_or_better_prob = 0.2 + (skill_factor * 0.4)  # Entre 0.33 y 0.66
                
                # Generar golpes
                rand = random.random()
                if rand < par_or_better_prob * 0.3:  # Birdie o mejor
                    stroke = par - random.randint(1, 2)
                elif rand < par_or_better_prob:  # Par
                    stroke = par
                else:  # Bogey o peor
                    stroke = par + random.randint(1, 3)
                
                strokes.append(stroke)
                
                # Calcular puntos
                # Para simplificar, usamos una fórmula básica: 2 puntos para par, +1 por debajo, -1 por encima
                point = 2 + (par - stroke)
                points.append(max(0, point))
                
                # Calcular Stableford
                # Fórmula: 2 puntos para par, +1 por cada golpe bajo par, 1 para bogey, 0 para doble bogey o peor
                stableford_point = 0
                if stroke <= par - 2:  # Eagle o mejor
                    stableford_point = 4
                elif stroke == par - 1:  # Birdie
                    stableford_point = 3
                elif stroke == par:  # Par
                    stableford_point = 2
                elif stroke == par + 1:  # Bogey
                    stableford_point = 1
                
                stableford.append(stableford_point)
            
            # Añadir la tarjeta a la base de datos
            scorecard_id = db.add_scorecard(
                player_id, 
                course_id, 
                date, 
                strokes,  
                points,  
                stableford,  
                handicap_coefficient_percent  # Almacenar el coeficiente (90, 95, 100) en lugar del hándicap calculado
            )
            
            print(f"Añadida tarjeta para {player_data['first_name']} {player_data['surname']} en {course_data['name']} ({date}) - ID: {scorecard_id}")

if __name__ == "__main__":
    # Asegurarse de que el directorio data existe
    os.makedirs('data', exist_ok=True)
    add_test_data()
