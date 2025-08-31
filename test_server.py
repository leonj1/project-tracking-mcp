#!/usr/bin/env python3
"""
Simple test script to verify the MCP server functionality
Run this to test basic operations without Claude Desktop
"""

from database import Database
from models import TaskStatus


def test_basic_operations():
    print("Testing Project Tracking MCP Server\n")
    print("=" * 50)
    
    # Initialize database
    db = Database("test_projects.db")
    
    # Test 1: Create projects
    print("\n1. Creating projects...")
    project1 = db.create_project("Web Redesign", "Complete website overhaul")
    print(f"   Created: {project1.name} (ID: {project1.id})")
    
    project2 = db.create_project("Mobile App", "New mobile application")
    print(f"   Created: {project2.name} (ID: {project2.id})")
    
    # Test 2: List projects
    print("\n2. Listing all projects...")
    projects = db.list_projects()
    for p in projects:
        print(f"   - {p.name}: {p.task_count} tasks")
    
    # Test 3: Add tasks
    print(f"\n3. Adding tasks to '{project1.name}'...")
    task1 = db.create_task(project1.id, "Design homepage mockup", "ux")
    print(f"   Added: {task1.description} [{task1.category}]")
    
    task2 = db.create_task(project1.id, "Implement responsive navigation", "frontend")
    print(f"   Added: {task2.description} [{task2.category}]")
    
    task3 = db.create_task(project1.id, "Write unit tests", "testing")
    print(f"   Added: {task3.description} [{task3.category}]")
    
    # Test 4: Update task status
    print("\n4. Updating task statuses...")
    updated_task = db.update_task_status(task1.id, "in_progress")
    print(f"   Task '{task1.description}' -> {updated_task.status}")
    
    updated_task = db.update_task_status(task2.id, "review")
    print(f"   Task '{task2.description}' -> {updated_task.status}")
    
    # Test 5: Get project details
    print(f"\n5. Getting project details for '{project1.name}'...")
    details = db.get_project(project1.id)
    if details:
        print(f"   Project: {details.name}")
        print(f"   Tasks: {len(details.tasks)}")
        print(f"   Stats: {details.task_stats}")
        print("\n   Task List:")
        for task in details.tasks:
            print(f"     - [{task.status:12}] {task.description} ({task.category})")
    
    # Test 6: Delete a task
    print("\n6. Deleting a task...")
    success = db.delete_task(task3.id)
    print(f"   Deleted task: {success}")
    
    # Test 7: Delete a project
    print(f"\n7. Deleting project '{project2.name}'...")
    success = db.delete_project(project2.id)
    print(f"   Deleted project: {success}")
    
    # Final list
    print("\n8. Final project list...")
    projects = db.list_projects()
    for p in projects:
        print(f"   - {p.name}: {p.task_count} tasks")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")


if __name__ == "__main__":
    test_basic_operations()