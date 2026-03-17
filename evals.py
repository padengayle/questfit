from ai_agents import extract_workout_with_gemini, generate_dungeon_master_narrative
from game_engine import Player
from google import genai
from google.genai import types
import time
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.getLogger("google").setLevel(logging.ERROR)
# 1. The Golden Dataset: A mix of edge cases and junk data
EVAL_CASES = [
    {
        "name": "The CrossFit Metcon",
        "input": "Did 5x5 back squats at 225lbs, then a 15 min AMRAP of 15 kettlebell swings and 10 burpees. Completed 4 rounds.",
        "expected_valid": True,
        "expected_exercise_count": 3
    },
    {
        "name": "The Pure Cardio",
        "input": "Ran 4 miles in Astoria today.",
        "expected_valid": True,
        "expected_exercise_count": 1
    },
    {
        "name": "The Junk Data",
        "input": "Can you give me a recipe for homemade chocoflan?",
        "expected_valid": False,
        "expected_exercise_count": 0
    }
]

def llm_as_a_judge(narrative: str) -> bool:
    """Uses Gemini strictly to grade the output of the Dungeon Master agent."""
    client = genai.Client()
    eval_prompt = f"""
    You are an objective AI grader. Evaluate this text: "{narrative}"
    Does this sound like an epic RPG Dungeon Master victory screen? 
    Reply strictly with the word YES or NO.
    """
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite-preview',
        contents=eval_prompt,
        config=types.GenerateContentConfig(temperature=0.0) 
    )
    return "YES" in response.text.upper()

def run_evaluations():
    print("🚀 Starting AI Pipeline Evaluations...\n")
    score = 0
    total = len(EVAL_CASES)
    
    for case in EVAL_CASES:
        print(f"Testing: {case['name']}")
        passed = True
        
        # Run the Extraction Agent
        result = extract_workout_with_gemini(case["input"])
        
        # 1. Deterministic Grading (Checking the exact JSON shape)
        if result.is_valid_workout != case["expected_valid"]:
            print(f"  ❌ Validity Failure: Expected {case['expected_valid']}, got {result.is_valid_workout}")
            passed = False
            
        if len(result.exercises) != case["expected_exercise_count"]:
            print(f"  ❌ Extraction Failure: Expected {case['expected_exercise_count']} exercises, got {len(result.exercises)}")
            passed = False
            
        # 2. Subjective Grading (LLM-as-a-judge for the creative output)
        if result.is_valid_workout:
            dummy_player = Player(name="Paden")
            narrative = generate_dungeon_master_narrative(dummy_player, result)
            is_epic = llm_as_a_judge(narrative)
            if not is_epic:
                print("  ❌ Tone Failure: The Dungeon Master narrative was not epic enough.")
                passed = False

        if passed:
            print("  ✅ PASS\n")
            score += 1
        else:
            print("  ❌ FAIL\n")
            
        # Quick sleep to avoid hitting API rate limits on the free tier
        time.sleep(2)

    print("========================================")
    print(f"🏁 Final Eval Score: {score}/{total} ({int((score/total)*100)}%)")
    print("========================================")

if __name__ == "__main__":
    run_evaluations()