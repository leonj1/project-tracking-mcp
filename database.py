import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from models import Project, Task, ProjectSummary, ProjectDetails


class Database:
    def __init__(self, db_path: str = "projects.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
    
    def _serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()
    
    def _deserialize_datetime(self, dt_str: str) -> datetime:
        return datetime.fromisoformat(dt_str)
    
    def list_projects(self) -> List[ProjectSummary]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.id, p.name, p.description, p.created_at, p.updated_at,
                       COUNT(t.id) as task_count
                FROM projects p
                LEFT JOIN tasks t ON p.id = t.project_id
                GROUP BY p.id
                ORDER BY p.updated_at DESC
            """)
            
            projects = []
            for row in cursor.fetchall():
                projects.append(ProjectSummary(
                    id=row[0],
                    name=row[1],
                    description=row[2] or "",
                    created_at=self._deserialize_datetime(row[3]),
                    updated_at=self._deserialize_datetime(row[4]),
                    task_count=row[5] or 0
                ))
            
            return projects
    
    def create_project(self, name: str, description: str = "") -> Project:
        project = Project(name=name, description=description)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO projects (id, name, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                project.id,
                project.name,
                project.description,
                self._serialize_datetime(project.created_at),
                self._serialize_datetime(project.updated_at)
            ))
            
            conn.commit()
        
        return project
    
    def get_project(self, project_id: str) -> Optional[ProjectDetails]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, created_at, updated_at
                FROM projects
                WHERE id = ?
            """, (project_id,))
            
            project_row = cursor.fetchone()
            if not project_row:
                return None
            
            cursor.execute("""
                SELECT id, description, category, status, created_at, updated_at
                FROM tasks
                WHERE project_id = ?
                ORDER BY created_at DESC
            """, (project_id,))
            
            tasks = []
            task_stats = {"backlog": 0, "in_progress": 0, "review": 0, "complete": 0}
            
            for task_row in cursor.fetchall():
                task = Task(
                    id=task_row[0],
                    description=task_row[1],
                    category=task_row[2],
                    status=task_row[3],
                    created_at=self._deserialize_datetime(task_row[4]),
                    updated_at=self._deserialize_datetime(task_row[5])
                )
                tasks.append(task)
                task_stats[task.status] += 1
            
            return ProjectDetails(
                id=project_row[0],
                name=project_row[1],
                description=project_row[2] or "",
                created_at=self._deserialize_datetime(project_row[3]),
                updated_at=self._deserialize_datetime(project_row[4]),
                tasks=tasks,
                task_stats=task_stats
            )
    
    def delete_project(self, project_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            
            conn.commit()
            
            return cursor.rowcount > 0
    
    def create_task(self, project_id: str, description: str, category: str) -> Optional[Task]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
            if not cursor.fetchone():
                return None
            
            task = Task(description=description, category=category)
            
            cursor.execute("""
                INSERT INTO tasks (id, project_id, description, category, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id,
                project_id,
                task.description,
                task.category,
                task.status,
                self._serialize_datetime(task.created_at),
                self._serialize_datetime(task.updated_at)
            ))
            
            cursor.execute("""
                UPDATE projects 
                SET updated_at = ? 
                WHERE id = ?
            """, (self._serialize_datetime(datetime.now()), project_id))
            
            conn.commit()
        
        return task
    
    def update_task_status(self, task_id: str, status: str) -> Optional[Task]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            now = datetime.now()
            cursor.execute("""
                UPDATE tasks 
                SET status = ?, updated_at = ?
                WHERE id = ?
            """, (status, self._serialize_datetime(now), task_id))
            
            if cursor.rowcount == 0:
                return None
            
            cursor.execute("""
                SELECT t.id, t.description, t.category, t.status, t.created_at, t.updated_at, t.project_id
                FROM tasks t
                WHERE t.id = ?
            """, (task_id,))
            
            task_row = cursor.fetchone()
            if not task_row:
                return None
            
            cursor.execute("""
                UPDATE projects 
                SET updated_at = ? 
                WHERE id = ?
            """, (self._serialize_datetime(now), task_row[6]))
            
            conn.commit()
            
            return Task(
                id=task_row[0],
                description=task_row[1],
                category=task_row[2],
                status=task_row[3],
                created_at=self._deserialize_datetime(task_row[4]),
                updated_at=self._deserialize_datetime(task_row[5])
            )
    
    def delete_task(self, task_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT project_id FROM tasks WHERE id = ?", (task_id,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            project_id = result[0]
            
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            
            cursor.execute("""
                UPDATE projects 
                SET updated_at = ? 
                WHERE id = ?
            """, (self._serialize_datetime(datetime.now()), project_id))
            
            conn.commit()
            
            return True