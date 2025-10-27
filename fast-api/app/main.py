from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List
import time
from collections import defaultdict
import os

from app.database import get_db
from app import models, schemas

app = FastAPI(
    title="Task Management API",
    description="FastAPI application with PostgreSQL for task management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting middleware
class RateLimiter:
    def __init__(self, calls: int = None, period: int = None):
        self.calls = calls or int(os.getenv("RATE_LIMIT_CALLS", "100"))
        self.period = period or int(os.getenv("RATE_LIMIT_PERIOD", "60"))
        self.requests = defaultdict(list)
    
    async def __call__(self, request: Request):
        client_ip = request.client.host
        now = time.time()
        
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.period
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.calls:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.calls} requests per {self.period} seconds."
            )
        
        self.requests[client_ip].append(now)


rate_limiter = RateLimiter()


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    await rate_limiter(request)
    response = await call_next(request)
    return response


@app.get("/")
async def root():
    return {
        "message": "Task Management API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# User endpoints
@app.post("/users", response_model=schemas.User, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users", response_model=List[schemas.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update username or email (corresponds to update_username.sql)"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/search/by-email", response_model=List[schemas.User])
def find_users_by_email(
    pattern: str = Query(..., description="Email pattern to search (e.g., '%@example.com')"),
    db: Session = Depends(get_db)
):
    """Find users with specific email pattern (corresponds to find_users.sql)"""
    users = db.query(models.User).filter(models.User.email.like(pattern)).all()
    return users


@app.get("/users/without-tasks", response_model=List[schemas.User])
def get_users_without_tasks(db: Session = Depends(get_db)):
    """Get users who have no tasks (corresponds to users_no_tasks.sql)"""
    users = db.query(models.User).outerjoin(models.Task).filter(models.Task.id == None).all()
    return users


@app.get("/users/with-task-count", response_model=List[schemas.UserWithTaskCount])
def get_users_with_task_count(db: Session = Depends(get_db)):
    """Get users and their task count (corresponds to users_task_count.sql)"""
    results = db.query(
        models.User.username,
        func.count(models.Task.id).label("task_count")
    ).outerjoin(models.Task).group_by(models.User.id, models.User.username).all()
    
    return [{"username": username, "task_count": count} for username, count in results]


@app.get("/users/with-in-progress-tasks", response_model=List[schemas.UserWithInProgressTask])
def get_users_with_in_progress_tasks(db: Session = Depends(get_db)):
    """Get users and their tasks with 'in progress' status (corresponds to users_in_progress.sql)"""
    results = db.query(
        models.User.username,
        models.Task.title,
        models.Task.description,
        models.Status.name.label("status")
    ).join(models.Task, models.User.id == models.Task.user_id)\
     .join(models.Status, models.Task.status_id == models.Status.id)\
     .filter(models.Status.name == "in progress").all()
    
    return [
        {
            "username": username,
            "title": title,
            "description": description,
            "status": status
        }
        for username, title, description, status in results
    ]


@app.get("/users/{user_id}/tasks", response_model=List[schemas.Task])
def get_user_tasks(user_id: int, db: Session = Depends(get_db)):
    """Get all tasks for a specific user (corresponds to user_tasks.sql)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tasks = db.query(models.Task).filter(models.Task.user_id == user_id).all()
    return tasks


# Status endpoints
@app.get("/statuses", response_model=List[schemas.Status])
def get_statuses(db: Session = Depends(get_db)):
    """Get all statuses"""
    statuses = db.query(models.Status).all()
    return statuses


# Task endpoints
@app.post("/tasks", response_model=schemas.Task, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Add a new task (corresponds to add_task.sql)"""
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == task.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify status exists
    status = db.query(models.Status).filter(models.Status.id == task.status_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks", response_model=List[schemas.Task])
def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tasks"""
    tasks = db.query(models.Task).offset(skip).limit(limit).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=schemas.TaskWithDetails)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task by ID with details"""
    task = db.query(models.Task).options(
        joinedload(models.Task.user),
        joinedload(models.Task.status)
    ).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update a task"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Verify status exists if status_id is being updated
    if "status_id" in update_data:
        status = db.query(models.Status).filter(models.Status.id == update_data["status_id"]).first()
        if not status:
            raise HTTPException(status_code=404, detail="Status not found")
    
    # Verify user exists if user_id is being updated
    if "user_id" in update_data:
        user = db.query(models.User).filter(models.User.id == update_data["user_id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


@app.patch("/tasks/{task_id}/status", response_model=schemas.Task)
def update_task_status(task_id: int, status_update: schemas.TaskStatusUpdate, db: Session = Depends(get_db)):
    """Update status of a specific task (corresponds to update_status.sql)"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify status exists
    status = db.query(models.Status).filter(models.Status.id == status_update.status_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    
    db_task.status_id = status_update.status_id
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a specific task (corresponds to delete_task.sql)"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return None


@app.get("/tasks/by-status/{status_name}", response_model=List[schemas.Task])
def get_tasks_by_status(status_name: str, db: Session = Depends(get_db)):
    """Get tasks by specific status (corresponds to tasks_by_status.sql)"""
    status = db.query(models.Status).filter(models.Status.name == status_name).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    
    tasks = db.query(models.Task).filter(models.Task.status_id == status.id).all()
    return tasks


@app.get("/tasks/incomplete", response_model=List[schemas.Task])
def get_incomplete_tasks(db: Session = Depends(get_db)):
    """Get all tasks that are not completed yet (corresponds to incomplete_tasks.sql)"""
    completed_status = db.query(models.Status).filter(models.Status.name == "completed").first()
    if not completed_status:
        raise HTTPException(status_code=404, detail="Completed status not found")
    
    tasks = db.query(models.Task).filter(models.Task.status_id != completed_status.id).all()
    return tasks


@app.get("/tasks/no-description", response_model=List[schemas.Task])
def get_tasks_without_description(db: Session = Depends(get_db)):
    """Get tasks without description (corresponds to tasks_no_description.sql)"""
    tasks = db.query(models.Task).filter(
        or_(models.Task.description == None, models.Task.description == "")
    ).all()
    return tasks


@app.get("/tasks/by-domain", response_model=List[schemas.Task])
def get_tasks_by_email_domain(
    domain: str = Query(..., description="Email domain to filter (e.g., '@example.com')"),
    db: Session = Depends(get_db)
):
    """Get tasks for users with specific email domain (corresponds to tasks_by_domain.sql)"""
    tasks = db.query(models.Task).join(models.User).filter(
        models.User.email.like(f"%{domain}")
    ).all()
    return tasks


# Statistics endpoints
@app.get("/stats/tasks-by-status", response_model=List[schemas.TaskCountByStatus])
def get_task_count_by_status(db: Session = Depends(get_db)):
    """Get task count for each status (corresponds to count_by_status.sql)"""
    results = db.query(
        models.Status.name,
        func.count(models.Task.id).label("task_count")
    ).outerjoin(models.Task).group_by(models.Status.name).all()
    
    return [{"name": name, "task_count": count} for name, count in results]

