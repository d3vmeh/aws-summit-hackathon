from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import Task
from datetime import datetime, timedelta

router = APIRouter()

# Mock data for MVP - will be replaced with task management API integrations
mock_tasks = [
    Task(
        id="1",
        title="Complete Math Homework",
        description="Chapter 5 problems 1-20",
        due_date=datetime.now() + timedelta(days=2),
        priority="high",
        completed=False
    ),
    Task(
        id="2",
        title="Study for Midterm",
        description="Review lecture notes and practice problems",
        due_date=datetime.now() + timedelta(days=3),
        priority="high",
        completed=False
    ),
    Task(
        id="3",
        title="Submit Lab Report",
        description="Physics lab on Newton's laws",
        due_date=datetime.now() - timedelta(days=1),  # Overdue
        priority="high",
        completed=False
    ),
    Task(
        id="4",
        title="Read Chapter 6",
        description="History textbook reading",
        due_date=datetime.now() + timedelta(days=5),
        priority="medium",
        completed=False
    ),
]

@router.get("/", response_model=List[Task])
async def get_tasks():
    """Get all tasks"""
    return mock_tasks

@router.post("/", response_model=Task)
async def create_task(task: Task):
    """Create a new task"""
    mock_tasks.append(task)
    return task

@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: str, task: Task):
    """Update a task"""
    for i, t in enumerate(mock_tasks):
        if t.id == task_id:
            mock_tasks[i] = task
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    for i, t in enumerate(mock_tasks):
        if t.id == task_id:
            mock_tasks.pop(i)
            return {"status": "deleted", "task_id": task_id}
    raise HTTPException(status_code=404, detail="Task not found")

@router.get("/sync/notion")
async def sync_notion():
    """Sync with Notion (placeholder)"""
    return {
        "status": "not_implemented",
        "message": "Notion API integration pending"
    }

@router.get("/sync/github")
async def sync_github():
    """Sync with GitHub (placeholder)"""
    return {
        "status": "not_implemented",
        "message": "GitHub API integration pending"
    }
