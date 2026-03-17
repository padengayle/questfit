from game_engine import Player, calculate_xp
from schemas import WorkoutExtraction, Exercise, ExerciseSet, ExerciseType

def test_calculate_xp_strength_and_metcon():
    """Test that the game engine correctly awards XP for a mixed workout."""
    
    # 1. Setup the initial state
    player = Player(name="Paden")
    
    # 2. Mock the exact clean data the AI Vision Extractor is required to output
    mock_ai_output = WorkoutExtraction(
        workout_summary="Heavy squats followed by a brutal AMRAP.",
        is_valid_workout=True,
        exercises=[
            Exercise(
                name="Back Squat",
                type=ExerciseType.STRENGTH,
                sets=[ExerciseSet(reps=5, weight_lbs=225.0)]
            ),
            Exercise(
                name="15 Min AMRAP",
                type=ExerciseType.METCON,
                sets=[ExerciseSet(duration_seconds=900)] # 15 minutes
            )
        ]
    )

    # 3. Run the deterministic game math
    updated_player = calculate_xp(mock_ai_output, player)

    # 4. Verify the exact arithmetic
    # Strength Math: (225 lbs * 5 reps) / 10 = 112.5 -> drops the decimal to 112
    assert updated_player.strength_xp == 112
    
    # Stamina Math: 900 seconds / 6 = 150
    assert updated_player.stamina_xp == 150
    
    # Agility was not trained, should be 0
    assert updated_player.agility_xp == 0
    
    # Total XP is 262. Threshold for Level 2 is 500, so player should still be Level 1
    assert updated_player.level == 1

def test_invalid_workout_ignored():
    """Test that junk data does not alter player stats."""
    player = Player(name="Paden")
    
    # Mock an AI output where the image was just a picture of a coffee cup
    mock_junk_output = WorkoutExtraction(
        workout_summary="Not a workout.",
        is_valid_workout=False,
        exercises=[]
    )
    
    updated_player = calculate_xp(mock_junk_output, player)
    
    # Stats should remain at baseline zero
    assert updated_player.strength_xp == 0
    assert updated_player.stamina_xp == 0