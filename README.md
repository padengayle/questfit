# QuestFit: Multi-Agent Fitness RPG Backend

QuestFit is an AI-powered FastAPI backend that transforms unstructured, messy fitness logs (like CrossFit AMRAPs or running logs) into structured RPG video game stats. 

Having worked in fast-paced startup environments, specifically on a data platform team at Bloomberg that was just 4 people, I designed this architecture to prioritize strict data contracts and robust error handling over basic prompt wrapping. This system treats LLMs as highly constrained reasoning engines rather than open-ended chatbots.

## 🧠 Core Architecture

This project utilizes a Level 2 Agentic Routing Workflow to separate non-deterministic reasoning from deterministic math.

1. The Receptionist (FastAPI + Pydantic): Enforces strict API contracts. If the input or AI output does not match the predefined schema, the request is dropped.
2. Agent 1: The Vision Extractor (Gemini 3.1 Flash Lite Preview): Operates at temperature=0.1. Ingests messy text or whiteboard photos and forces the unstructured data into a rigid JSON structure using the GenAI SDK's response_schema constraint.
3. The Deterministic Bridge (Python State Machine): LLMs are poor at arithmetic. The extracted JSON is passed to a standard Python game engine to reliably calculate Experience Points (XP) and level-ups without hallucinations.
4. Agent 2: The Dungeon Master (Gemini 3.1 Flash Lite Preview): Operates at temperature=0.7. Takes the dynamically calculated RPG stats and writes a highly personalized, two-sentence victory screen using dynamic context injection.

## 🧪 Testing & Evals

Production AI requires production testing. This repository utilizes a hybrid testing approach:

* Unit Testing (pytest): Validates the FastAPI routing and the Python Game Engine by fully mocking the LLM API calls, ensuring standard CI/CD pipelines run cleanly without draining API budgets.
* LLM-as-a-Judge (evals.py): An automated evaluation script that tests the pipeline against a golden dataset of edge cases (e.g., junk data, CrossFit AMRAPs) using a zero-temperature model to grade the narrative tone and extraction accuracy.

## 🚀 How to Run Locally

1. Clone and setup the environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

2. Add your API Key
Create a .env file in the root directory:
GEMINI_API_KEY=your_google_api_key_here

3. Run the Evaluation Suite
Verify the models are accurately extracting data and matching the required tone:
python evals.py

4. Start the Live Server
Boot up the interactive Swagger UI to test real workout logs:
fastapi dev main.py

Navigate to http://127.0.0.1:8000/docs to test the /process-workout endpoint.