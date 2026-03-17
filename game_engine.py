from schemas import WorkoutExtraction, ExerciseType

class Player:
    def __init__(self, name: str = "Player One"):
        self.name = name
        self.level = 1
        self.strength_xp = 0
        self.stamina_xp = 0
        self.agility_xp = 0
        
    def __str__(self):
        return f"Lvl {self.level} {self.name} | STR: {self.strength_xp} | STA: {self.stamina_xp} | AGI: {self.agility_xp}"

def calculate_xp(workout_data: WorkoutExtraction, player: Player) -> Player:
    """
    Takes the strictly formatted AI output and applies deterministic game math.
    """
    if not workout_data.is_valid_workout:
        return player

    for exercise in workout_data.exercises:
        for subset in exercise.sets:
            if exercise.type == ExerciseType.STRENGTH:
                weight = subset.weight_lbs or 0
                reps = subset.reps or 0
                # Math: (Weight x Reps) / 10
                player.strength_xp += int((weight * reps) / 10)
            
            elif exercise.type == ExerciseType.METCON:
                duration = subset.duration_seconds or 0
                # Math: 10 XP per minute (60 seconds) of metcon
                player.stamina_xp += int(duration / 6)
                # Bonus Math: Calculate total reps if rounds are provided
                if exercise.rounds:
                    reps = subset.reps or 0
                    total_reps = int(reps * exercise.rounds)
                    # Award 1 extra Stamina XP for every 2 reps completed in the AMRAP
                    player.stamina_xp += int(total_reps / 2)
                
            elif exercise.type == ExerciseType.CARDIO:
                distance = subset.distance_miles or 0
                # Math: 50 XP per mile
                player.agility_xp += int(distance * 50)
    
    # Basic Level Up Logic: Every 500 total XP grants a new level
    total_xp = player.strength_xp + player.stamina_xp + player.agility_xp
    player.level = 1 + (total_xp // 500)
    
    return player