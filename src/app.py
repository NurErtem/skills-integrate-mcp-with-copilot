"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory users database (passwords are bcrypt-hashed)
users_db = {
    "admin@mergington.edu": {
        "name": "Administrator",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin",
        "grade": None
    },
    "principal@mergington.edu": {
        "name": "Principal",
        "hashed_password": pwd_context.hash("principal123"),
        "role": "admin",
        "grade": None
    }
}


class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: str = "student"
    grade: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    grade: Optional[str] = None


class ActivityCreate(BaseModel):
    name: str
    description: str
    schedule: str
    max_participants: int


class ActivityUpdate(BaseModel):
    description: Optional[str] = None
    schedule: Optional[str] = None
    max_participants: Optional[int] = None


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Authenticate user via HTTP Basic Auth"""
    user = users_db.get(credentials.username)
    if not user or not pwd_context.verify(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"email": credentials.username, **user}


def require_admin(current_user: dict = Depends(get_current_user)):
    """Require admin role for access"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


# ── Admin: User Management ──────────────────────────────────────────────────

@app.get("/admin/users", tags=["Admin"])
def list_users(admin: dict = Depends(require_admin)):
    """List all users (admin only)"""
    return [
        {"email": email, "name": u["name"], "role": u["role"], "grade": u["grade"]}
        for email, u in users_db.items()
    ]


@app.post("/admin/users", status_code=status.HTTP_201_CREATED, tags=["Admin"])
def create_user(user: UserCreate, admin: dict = Depends(require_admin)):
    """Create a new user (admin only)"""
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    if user.role not in ("admin", "student", "teacher"):
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin', 'teacher', or 'student'")
    users_db[user.email] = {
        "name": user.name,
        "hashed_password": pwd_context.hash(user.password),
        "role": user.role,
        "grade": user.grade,
    }
    return {"message": f"User {user.email} created", "email": user.email, "role": user.role}


@app.put("/admin/users/{email}", tags=["Admin"])
def update_user(email: str, update: UserUpdate, admin: dict = Depends(require_admin)):
    """Update an existing user (admin only)"""
    if email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    if update.role is not None and update.role not in ("admin", "student", "teacher"):
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin', 'teacher', or 'student'")
    user = users_db[email]
    if update.name is not None:
        user["name"] = update.name
    if update.password is not None:
        user["hashed_password"] = pwd_context.hash(update.password)
    if update.role is not None:
        user["role"] = update.role
    if update.grade is not None:
        user["grade"] = update.grade
    return {"message": f"User {email} updated"}


@app.delete("/admin/users/{email}", tags=["Admin"])
def delete_user(email: str, admin: dict = Depends(require_admin)):
    """Delete a user (admin only)"""
    if email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    if email == admin["email"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own admin account")
    # Ensure at least one admin account always remains
    target_role = users_db[email]["role"]
    if target_role == "admin":
        remaining_admins = sum(1 for u in users_db.values() if u["role"] == "admin") - 1
        if remaining_admins < 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last admin account")
    del users_db[email]
    return {"message": f"User {email} deleted"}


# ── Admin: Activity Management ──────────────────────────────────────────────

@app.post("/admin/activities", status_code=status.HTTP_201_CREATED, tags=["Admin"])
def create_activity(activity: ActivityCreate, admin: dict = Depends(require_admin)):
    """Create a new activity (admin only)"""
    if activity.name in activities:
        raise HTTPException(status_code=400, detail="Activity already exists")
    if activity.max_participants < 1:
        raise HTTPException(status_code=400, detail="max_participants must be at least 1")
    activities[activity.name] = {
        "description": activity.description,
        "schedule": activity.schedule,
        "max_participants": activity.max_participants,
        "participants": [],
    }
    return {"message": f"Activity '{activity.name}' created"}


@app.put("/admin/activities/{activity_name}", tags=["Admin"])
def update_activity(activity_name: str, update: ActivityUpdate, admin: dict = Depends(require_admin)):
    """Update an existing activity (admin only)"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    if update.max_participants is not None and update.max_participants < 1:
        raise HTTPException(status_code=400, detail="max_participants must be at least 1")
    activity = activities[activity_name]
    if update.max_participants is not None and update.max_participants < len(activity["participants"]):
        raise HTTPException(
            status_code=400,
            detail=f"max_participants cannot be less than the current number of participants ({len(activity['participants'])})"
        )
    if update.description is not None:
        activity["description"] = update.description
    if update.schedule is not None:
        activity["schedule"] = update.schedule
    if update.max_participants is not None:
        activity["max_participants"] = update.max_participants
    return {"message": f"Activity '{activity_name}' updated"}


@app.delete("/admin/activities/{activity_name}", tags=["Admin"])
def delete_activity(activity_name: str, admin: dict = Depends(require_admin)):
    """Delete an activity (admin only)"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    del activities[activity_name]
    return {"message": f"Activity '{activity_name}' deleted"}
