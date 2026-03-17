from google import genai
from google.genai import types
from schemas import WorkoutExtraction
from game_engine import Player
import time
import os
from dotenv import load_dotenv


load_dotenv()

def extract_workout_with_gemini(user_text: str, image_file=None) -> WorkoutExtraction:
    """
    Takes the messy user input and forces Gemini to return our exact Pydantic schema
    using the modern google.genai SDK.
    """
    start_time = time.time()
    client = genai.Client() 
    
    prompt = """
    You are an expert fitness data extraction agent. 
    Review the provided workout log or image. 
    Extract the exercises, sets, reps, and weights. 
    Categorize each exercise strictly as STRENGTH, CARDIO, METCON, or MOBILITY.
    CRITICAL RULE FOR CIRCUITS AND AMRAPS: If the user completes multiple "rounds", translate that directly into sets. For example, 4 rounds of 15 kettlebell swings must be extracted as 4 individual sets of 15 reps.
    If the input is not a workout, set is_valid_workout to false.
    """
    
    contents = [prompt]
    if user_text:
        contents.append(f"User Log: {user_text}")
        
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite-preview',
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=WorkoutExtraction,
            temperature=0.1 
        )
    )
    
    elapsed_time = time.time() - start_time
    print(f"[TELEMETRY] Gemini Extraction complete in {elapsed_time:.2f} seconds")
    
    return WorkoutExtraction.model_validate_json(response.text)

def generate_dungeon_master_narrative(player: Player, workout: WorkoutExtraction) -> str:
    """
    Takes the deterministic game state and uses Gemini to write a personalized RPG victory screen.
    """
    start_time = time.time()
    client = genai.Client()
    
    prompt = f"""
    You are an AI Dungeon Master for a fitness RPG.
    The player's name is {player.name}.
    They just completed this workout: {workout.workout_summary}
    
    Their updated RPG stats are:
    Level: {player.level}
    Strength XP: {player.strength_xp}
    Stamina XP: {player.stamina_xp}
    Agility XP: {player.agility_xp}
    
    Write a punchy, two sentence epic RPG victory screen narrative celebrating their workout and current stats. 
    Keep it highly thematic, encouraging, and do not use dashes.
    """
    
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite-preview',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7 
        )
    )
    
    elapsed_time = time.time() - start_time
    print(f"[TELEMETRY] Dungeon Master Narrative generated in {elapsed_time:.2f} seconds")
    
    return response.text.strip()