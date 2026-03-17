from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# Define strict categories so the Game Engine knows which XP to award
class ExerciseType(str, Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    METCON = "metcon" 
    MOBILITY = "mobility"

# Handle the messy reality of different workout metrics
class ExerciseSet(BaseModel):
    reps: Optional[int] = Field(None, description="Number of repetitions performed")
    weight_lbs: Optional[float] = Field(None, description="Weight used in pounds")
    duration_seconds: Optional[int] = Field(None, description="Duration in seconds")
    distance_miles: Optional[float] = Field(None, description="Distance covered in miles")

# Group the sets under a specific movement
class Exercise(BaseModel):
    name: str = Field(..., description="Standardized name of the exercise, e.g., 'Back Squat' or 'Rowing'")
    type: ExerciseType = Field(..., description="The category of the exercise")
    sets: List[ExerciseSet] = Field(default_factory=list, description="List of sets completed")    
    rounds: Optional[int] = Field(None, description= "Number of rounds done. typnicall in an AMRAP or Fortime workout")
    
class WorkoutExtraction(BaseModel):
    workout_summary: str = Field(..., description="A brief 1-sentence summary of the workout vibe")
    exercises: List[Exercise] = Field(..., description="List of all exercises performed")
    is_valid_workout: bool = Field(..., description="True if the input contained a real workout, False if it was junk data")
    quest_narrative: Optional[str] = Field(None, description="The AI Dungeon Master's personalized victory screen")
    current_level: Optional[int] = Field(default=None, description="The user's newly calculated RPG level.")
    total_xp: Optional[int] = Field(default=None, description="The user's newly calculated experience points")