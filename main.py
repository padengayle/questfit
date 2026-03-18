import os
import time
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select

from schemas import WorkoutExtraction
from ai_agents import extract_workout_with_gemini, generate_dungeon_master_narrative
from game_engine import Player, calculate_xp

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

# 1. Database Setup
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    level: int = 1
    total_xp: int = 0
    
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_or_create_paden(session: Session):
    user = session.exec(select(User).where(User.name == "Paden")).first()
    if not user:
        user = User(name="Paden", level=1, total_xp=0)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

# This helper opens a secure connection to Neon for every request
def get_session():
    with Session(engine) as session:
        yield session

# 2. Server Startup Event
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

# 3. App Initialization
app = FastAPI(
    title="QuestFit API", 
    description="An AI-powered backend that turns unstructured workouts into RPG stats.",
    lifespan=lifespan
)
# Initialize the rate limiter to track IP addresses
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 4. Endpoints
@app.get("/player-status")
def get_player_status(session: Session = Depends(get_session)):
    # Fetch your profile from the database
    db_user = get_or_create_paden(session)
    
    return {
        "name": db_user.name,
        "level": db_user.level,
        "total_xp": db_user.total_xp
    }

@limiter.limit("15/day")
@app.post("/process-workout", response_model=WorkoutExtraction)
async def process_workout(
    text_log: str = Form(None),
    image: UploadFile = File(None),
    session: Session = Depends(get_session) # Injects the database connection
):
    start_time = time.time()

    if not text_log and not image:
        raise HTTPException(status_code=400, detail="You must provide either a text log or an image of your workout.")

    # Step 1: The Vision Extractor
    try:
        extraction = extract_workout_with_gemini(user_text=text_log, image_file=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Extraction failed: {str(e)}")

    # Step 2: Fetch your saved character from Neon Postgres
    db_user = get_or_create_paden(session)
    
    # Load your saved stats into the Game Engine
    current_player = Player(name=db_user.name, level=db_user.level, total_xp=db_user.total_xp)

    # Step 3: The Deterministic Game Engine
    updated_player = calculate_xp(extraction, current_player)
    
    # Step 4: Save the new progress back to the database
    db_user.level = updated_player.level
    db_user.total_xp = updated_player.total_xp
    session.add(db_user)
    session.commit()
    
    # Step 5: The AI Dungeon Master
    if extraction.is_valid_workout:
        narrative = generate_dungeon_master_narrative(updated_player, extraction)
        extraction.quest_narrative = narrative
        
    extraction.current_level = updated_player.level
    extraction.total_xp = updated_player.total_xp

    elapsed_time = time.time() - start_time
    print(f"\n[TELEMETRY] Total Pipeline Latency: {elapsed_time:.2f} seconds\n")

    return extraction