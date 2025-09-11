import json
import pathlib
from typing import List, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Configuration ---
WORKOUT_DATA_FILE = pathlib.Path("workout_data.json")

# --- Pydantic Models (Data Validation) ---
class WorkoutLog(BaseModel):
    date: str
    type: str
    weight: float
    reps: int
    notes: Optional[str] = None
    photo: Optional[str] = None

# --- FastAPI App Initialization ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper Functions ---
def read_json_file(file_path: pathlib.Path) -> Dict:
    if not file_path.exists():
        return {}
    with open(file_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def write_json_file(file_path: pathlib.Path, data: Dict):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# --- API Endpoints ---

@app.get("/users", response_model=List[str])
def get_users():
    """Returns a list of all users who have logs."""
    workout_data = read_json_file(WORKOUT_DATA_FILE)
    return list(workout_data.keys())

@app.get("/logs/{username}", response_model=List[WorkoutLog])
def get_logs_for_user(username: str):
    """Returns all workout logs for a specific user."""
    workout_data = read_json_file(WORKOUT_DATA_FILE)
    return workout_data.get(username, [])

@app.post("/logs/{username}", response_model=WorkoutLog)
def add_log_for_user(username: str, log: WorkoutLog):
    """Adds a new workout log for a specific user."""
    workout_data = read_json_file(WORKOUT_DATA_FILE)
    user_logs = workout_data.get(username, [])
    user_logs.append(log.dict())
    workout_data[username] = user_logs
    write_json_file(WORKOUT_DATA_FILE, workout_data)
    return log

@app.get("/")
def read_root():
    return {"message": "Welcome to the Muscle Growth API"}