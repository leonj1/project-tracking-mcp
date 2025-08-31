# Project Tracking MCP Server

A lightweight Model Context Protocol (MCP) server built with FastMCP that provides project and task management capabilities through a single SQLite database file.

## Features

- **Project Management**
  - Create, list, get, and delete projects
  - Each project has a name, description, and timestamps
  
- **Task Management**
  - Add tasks to projects with descriptions and categories
  - Track task status: `backlog`, `in_progress`, `review`, `complete`
  - Update task status and delete tasks
  - Categories for organizing tasks (e.g., 'testing', 'ux', 'transcription')

- **Single-File Database**
  - All data stored in a single SQLite file (`projects.db`)
  - Automatic database initialization
  - Persistent storage with full CRUD operations

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd project-tracking-mcp
```

2. Install dependencies using one of these methods:

Using pip:
```bash
pip install -r requirements.txt
```

Using uv (recommended for FastMCP):
```bash
uv pip install fastmcp pydantic
```

Or install directly:
```bash
pip install fastmcp pydantic
```

## Usage

### Running the Server

Start the MCP server:
```bash
python server.py
```

### Configuring with Claude Desktop

Add this configuration to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "project-tracker": {
      "command": "python",
      "args": ["/path/to/project-tracking-mcp/server.py"]
    }
  }
}
```

Or use FastMCP's automatic installation:
```bash
fastmcp install claude-desktop server.py --server-name "Project Tracker"
```

## Available MCP Tools

### Project Management

- **`list_projects()`**: List all projects with summary information
- **`create_project(name, description?)`**: Create a new project
- **`get_project(project_id)`**: Get detailed project information with all tasks
- **`delete_project(project_id)`**: Delete a project and all its tasks

### Task Management

- **`create_task(project_id, description, category)`**: Add a task to a project
- **`update_task_status(task_id, status)`**: Update task status
- **`delete_task(task_id)`**: Delete a task

### Statistics

- **`get_project_stats()`**: Get overall statistics about projects and tasks

## Example Usage

### Create a Project
```python
create_project(
    name="Website Redesign",
    description="Complete overhaul of company website"
)
```

### Add Tasks
```python
create_task(
    project_id="<project-id>",
    description="Design new homepage mockup",
    category="ux"
)
```

### Update Task Status
```python
update_task_status(
    task_id="<task-id>",
    status="in_progress"
)
```

### Get Project with Tasks
```python
get_project(project_id="<project-id>")
# Returns project details with all tasks and statistics
```

## Data Models

### Project
- `id`: Unique identifier (UUID)
- `name`: Project name
- `description`: Project description
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `tasks`: List of associated tasks

### Task
- `id`: Unique identifier (UUID)
- `description`: Task description
- `category`: Task category/label
- `status`: Current status (backlog/in_progress/review/complete)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Database

The server uses SQLite with two tables:
- `projects`: Stores project information
- `tasks`: Stores task information with foreign key to projects

The database file (`projects.db`) is created automatically on first run.

## Requirements

- Python 3.10+
- FastMCP
- Pydantic 2.0+
- SQLite (built-in with Python)

## License

MIT