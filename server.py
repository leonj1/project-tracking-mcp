#!/usr/bin/env python3
from fastmcp import FastMCP
from typing import List, Optional
from models import (
    Project, Task, ProjectSummary, ProjectDetails,
    CreateProjectInput, CreateTaskInput, UpdateTaskStatusInput,
    OperationResponse, TaskStatus
)
from database import Database


mcp = FastMCP("Project Tracker")
db = Database()


@mcp.tool
def list_projects() -> List[ProjectSummary]:
    """List all existing projects with summary information"""
    return db.list_projects()


@mcp.tool
def create_project(name: str, description: Optional[str] = "") -> Project:
    """Create a new project
    
    Args:
        name: The name of the project
        description: Optional description of the project
    
    Returns:
        The created project with its ID and metadata
    """
    if not name or not name.strip():
        raise ValueError("Project name cannot be empty")
    
    return db.create_project(name.strip(), description or "")


@mcp.tool
def get_project(project_id: str) -> ProjectDetails:
    """Get a project with all its tasks
    
    Args:
        project_id: The unique ID of the project
    
    Returns:
        Detailed project information including all tasks
    """
    project = db.get_project(project_id)
    if not project:
        raise ValueError(f"Project with ID {project_id} not found")
    
    return project


@mcp.tool
def delete_project(project_id: str) -> OperationResponse:
    """Delete a project and all its tasks
    
    Args:
        project_id: The unique ID of the project to delete
    
    Returns:
        Operation result with success status and message
    """
    success = db.delete_project(project_id)
    
    if success:
        return OperationResponse(
            success=True,
            message=f"Project {project_id} deleted successfully"
        )
    else:
        return OperationResponse(
            success=False,
            message=f"Project with ID {project_id} not found"
        )


@mcp.tool
def create_task(
    project_id: str,
    description: str,
    category: str
) -> Task:
    """Add a task to a project
    
    Args:
        project_id: The ID of the project to add the task to
        description: Description of the task
        category: Category label (e.g., 'testing', 'ux', 'transcription')
    
    Returns:
        The created task with its ID and metadata
    """
    if not description or not description.strip():
        raise ValueError("Task description cannot be empty")
    
    if not category or not category.strip():
        raise ValueError("Task category cannot be empty")
    
    task = db.create_task(project_id, description.strip(), category.strip())
    
    if not task:
        raise ValueError(f"Project with ID {project_id} not found")
    
    return task


@mcp.tool
def update_task_status(task_id: str, status: TaskStatus) -> Task:
    """Update the status of a task
    
    Args:
        task_id: The unique ID of the task
        status: New status ('backlog', 'in_progress', 'review', 'complete')
    
    Returns:
        The updated task with new status
    """
    valid_statuses = ["backlog", "in_progress", "review", "complete"]
    if status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    task = db.update_task_status(task_id, status)
    
    if not task:
        raise ValueError(f"Task with ID {task_id} not found")
    
    return task


@mcp.tool
def delete_task(task_id: str) -> OperationResponse:
    """Delete a task from a project
    
    Args:
        task_id: The unique ID of the task to delete
    
    Returns:
        Operation result with success status and message
    """
    success = db.delete_task(task_id)
    
    if success:
        return OperationResponse(
            success=True,
            message=f"Task {task_id} deleted successfully"
        )
    else:
        return OperationResponse(
            success=False,
            message=f"Task with ID {task_id} not found"
        )


@mcp.tool
def get_project_stats() -> dict:
    """Get overall statistics about all projects and tasks
    
    Returns:
        Dictionary with project and task statistics
    """
    projects = db.list_projects()
    
    total_tasks = sum(p.task_count for p in projects)
    
    stats = {
        "total_projects": len(projects),
        "total_tasks": total_tasks,
        "projects_with_tasks": sum(1 for p in projects if p.task_count > 0),
        "empty_projects": sum(1 for p in projects if p.task_count == 0)
    }
    
    if projects:
        stats["average_tasks_per_project"] = round(total_tasks / len(projects), 2)
    else:
        stats["average_tasks_per_project"] = 0
    
    return stats


if __name__ == "__main__":
    mcp.run()