from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from schemas import WorkoutExtraction
from ai_agents import extract_workout_with_gemini, generate_dungeon_master_narrative
from game_engine import Player, calculate_xp
import time

app = FastAPI(
    title="QuestFit API", 
    description="An AI-powered backend that turns unstructured workouts into RPG stats."
)

# Hardcoding the player name to Paden
current_player = Player(name="Paden")

@app.post("/process-workout", response_model=WorkoutExtraction)
async def process_workout(
    text_log: str = Form(None),
    image: UploadFile = File(None)
):
    start_time = time.time()

    if not text_log and not image:
        raise HTTPException(status_code=400, detail="You must provide either a text log or an image of your workout.")

    # Step 1: The Vision Extractor
    try:
        extraction = extract_workout_with_gemini(user_text=text_log, image_file=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Extraction failed: {str(e)}")

    # Step 2: The Deterministic Game Engine
    global current_player
    current_player = calculate_xp(extraction, current_player)
    
    # Step 3: The AI Dungeon Master
    if extraction.is_valid_workout:
        narrative = generate_dungeon_master_narrative(current_player, extraction)
        extraction.quest_narrative = narrative

    elapsed_time = time.time() - start_time
    print(f"\n[TELEMETRY] Total Pipeline Latency: {elapsed_time:.2f} seconds\n")

    return extraction