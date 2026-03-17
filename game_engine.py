from schemas import WorkoutExtraction, ExerciseType

class Player:
    def __init__(self, name: str = "Player One", level: int = 1, strength_xp: int = 0, stamina_xp: int = 0, agility_xp: int = 0, total_xp:int = 0):
        self.name = name
        self.level = level
        self.strength_xp = strength_xp
        self.stamina_xp = stamina_xp
        self.agility_xp = agility_xp
        self.total_xp = total_xp
        
    def __str__(self):
        return f"Lvl {self.level} {self.name} | STR: {self.strength_xp} | STA: {self.stamina_xp} | AGI: {self.agility_xp}"

def calculate_xp(workout_data: WorkoutExtraction, player: Player) -> Player:
    """
    Takes the strictly formatted AI output and applies deterministic game math.
    """
    if not workout_data.is_valid_workout:
        return player

    for exercise in workout_data.exercises:
        # Default to 1 round if the AI doesn't specify any
        rounds = exercise.rounds if exercise.rounds else 1
        
        for subset in exercise.sets:
            if exercise.type == ExerciseType.STRENGTH:
                weight = subset.weight_lbs or 0
                reps = subset.reps or 0
                player.strength_xp += int(((weight * reps) / 10) * rounds)
            
            elif exercise.type == ExerciseType.METCON:
                duration = subset.duration_seconds or 0
                player.stamina_xp += int((duration / 6) * rounds)
                
                reps = subset.reps or 0
                total_reps = int(reps * rounds)
                player.stamina_xp += int(total_reps / 2)
                
            elif exercise.type == ExerciseType.CARDIO:
                distance = subset.distance_miles or 0
                player.agility_xp += int((distance * 50) * rounds)
    
    # FIX: Calculate the XP gained from just this workout
    session_xp = player.strength_xp + player.stamina_xp + player.agility_xp
    
    # FIX: Add the session XP to the lifetime total from the database
    player.total_xp += session_xp
    
    # Basic Level Up Logic: Every 500 total XP grants a new level
    player.level = 1 + (player.total_xp // 500)
    
    return player