from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from schemas import WorkoutExtraction

client = TestClient(app)

def test_process_workout_no_input():
    response = client.post("/process-workout")
    assert response.status_code == 400

# We stack the decorators to mock both functions
@patch("main.generate_dungeon_master_narrative")
@patch("main.extract_workout_with_gemini")
def test_process_workout_mock_success(mock_gemini_call, mock_dungeon_master):
    
    # Force the mock extractor to return a perfect Pydantic object
    mock_gemini_call.return_value = WorkoutExtraction(
        workout_summary="Mocked 3 mile run.",
        is_valid_workout=True,
        exercises=[]
    )
    
    # Force the mock Dungeon Master to return a fake story
    mock_dungeon_master.return_value = "Paden conquered the asphalt! Agility increased."
    
    response = client.post("/process-workout", data={"text_log": "Ran 3 miles"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid_workout"] == True
    assert data["quest_narrative"] == "Paden conquered the asphalt! Agility increased."
    
    # Prove both agents were called
    mock_gemini_call.assert_called_once()
    mock_dungeon_master.assert_called_once()