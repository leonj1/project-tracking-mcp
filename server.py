#!/usr/bin/env python3
import argparse
from pathlib import Path
from fastmcp import FastMCP
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
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


# Pydantic models for API requests
class CreateTaskRequest(BaseModel):
    description: str
    category: str

class UpdateTaskStatusRequest(BaseModel):
    status: str


# HTTP Server setup
def create_app(enable_web: bool = True):
    """Create FastAPI application with optional web interface"""
    
    # Create FastAPI app
    app = FastAPI(
        title="Project Tracker",
        description="Project and task management with MCP support",
        version="1.0.0"
    )
    
    if enable_web:
        # Add CORS middleware for development
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup templates and static files
        templates_dir = Path(__file__).parent / "templates"
        static_dir = Path(__file__).parent / "static"
        
        # Create directories if they don't exist
        templates_dir.mkdir(exist_ok=True)
        static_dir.mkdir(exist_ok=True)
        
        templates = Jinja2Templates(directory=str(templates_dir))
        
        # Mount static files
        if static_dir.exists():
            app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Web interface routes
        @app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Main dashboard page"""
            projects = db.list_projects()
            total_tasks = sum(p.task_count for p in projects)
            
            stats = {
                "total_projects": len(projects),
                "total_tasks": total_tasks,
                "projects_with_tasks": sum(1 for p in projects if p.task_count > 0),
                "empty_projects": sum(1 for p in projects if p.task_count == 0),
                "average_tasks_per_project": round(total_tasks / len(projects), 2) if projects else 0
            }
            
            return templates.TemplateResponse("dashboard.html", {
                "request": request,
                "projects": projects,
                "stats": stats,
                "title": "Project Dashboard"
            })
        
        @app.get("/project/{project_id}", response_class=HTMLResponse)
        async def project_detail(request: Request, project_id: str):
            """Project detail page"""
            try:
                project = db.get_project(project_id)
                if not project:
                    raise HTTPException(status_code=404, detail="Project not found")
                
                return templates.TemplateResponse("project_detail.html", {
                    "request": request,
                    "project": project,
                    "title": f"Project: {project.name}"
                })
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
        
        # API routes (REST endpoints for web interface)
        @app.get("/api/projects", response_model=List[ProjectSummary])
        async def api_list_projects():
            """API endpoint for listing projects"""
            return db.list_projects()
        
        @app.get("/api/project/{project_id}", response_model=ProjectDetails)
        async def api_get_project(project_id: str):
            """API endpoint for getting project details"""
            project = db.get_project(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            return project
        
        @app.put("/api/task/{task_id}/status", response_model=Task)
        async def api_update_task_status(task_id: str, status_data: UpdateTaskStatusRequest):
            """API endpoint for updating task status"""
            valid_statuses = ["backlog", "in_progress", "review", "complete"]
            if status_data.status not in valid_statuses:
                raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            
            task = db.update_task_status(task_id, status_data.status)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            return task
        
        @app.post("/api/project/{project_id}/tasks", response_model=Task)
        async def api_create_task(project_id: str, task_data: CreateTaskRequest):
            """API endpoint for creating tasks"""
            if not task_data.description or not task_data.description.strip():
                raise HTTPException(status_code=400, detail="Task description cannot be empty")
            
            if not task_data.category or not task_data.category.strip():
                raise HTTPException(status_code=400, detail="Task category cannot be empty")
            
            task = db.create_task(project_id, task_data.description.strip(), task_data.category.strip())
            if not task:
                raise HTTPException(status_code=404, detail="Project not found")
            return task
        
        @app.get("/api/stats")
        async def api_get_stats():
            """API endpoint for project statistics"""
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
    
    # Mount MCP server
    mcp_app = mcp.http_app()
    app.mount("/mcp", mcp_app)
    
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Project Tracker Server")
    parser.add_argument("--mcp-only", action="store_true", 
                       help="Run in MCP-only mode (no web interface)")
    parser.add_argument("--host", default="127.0.0.1", 
                       help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, 
                       help="Port to bind to (default: 8000)")
    
    args = parser.parse_args()
    
    if args.mcp_only:
        # Run MCP server only
        mcp.run()
    else:
        # Run HTTP server with web interface and MCP
        import uvicorn
        app = create_app(enable_web=True)
        uvicorn.run(app, host=args.host, port=args.port)