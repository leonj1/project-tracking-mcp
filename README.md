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

### Configuring with Claude Code

To use this MCP server with Claude Code (Anthropic's official CLI):

1. **Install Claude Code** (if you haven't already):
   ```bash
   # Install via pip
   pip install claude-code
   
   # Or using uv
   uv tool install claude-code
   ```

2. **Add MCP server to Claude Code configuration**:
   
   Create or edit your Claude Code MCP configuration file:
   ```bash
   # Create the config directory if it doesn't exist
   mkdir -p ~/.claude
   
   # Edit the MCP config file
   nano ~/.claude/mcp_servers.json
   ```

3. **Add this server configuration**:
   ```json
   {
     "project-tracker": {
       "command": "python",
       "args": ["/absolute/path/to/project-tracking-mcp/server.py", "--mcp-only"],
       "env": {}
     }
   }
   ```

4. **Update the path** in the configuration to point to your actual installation directory:
   ```json
   {
     "project-tracker": {
       "command": "python",
       "args": ["/home/yourusername/project-tracking-mcp/server.py", "--mcp-only"],
       "env": {}
     }
   }
   ```

5. **Verify the installation**:
   ```bash
   # Test that Claude Code can connect to the server
   claude-code --list-tools
   ```
   
   You should see the project tracking tools listed:
   - `list_projects`
   - `create_project` 
   - `get_project`
   - `delete_project`
   - `create_task`
   - `update_task_status`
   - `delete_task`
   - `get_project_stats`

6. **Start using with Claude Code**:
   ```bash
   # Start Claude Code session
   claude-code
   
   # Now you can use project tracking commands like:
   # "Create a new project called 'My Web App'"
   # "Add a task to implement user authentication"
   # "Show me all my projects and their tasks"
   ```

**Note**: The `--mcp-only` flag ensures the server runs in MCP mode without starting the HTTP web interface, which is optimal for Claude Code integration.

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