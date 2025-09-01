# User Interface for Project and Task Viewing

## Feature Overview

Add a web-based user interface that allows users to visually view and interact with their projects and tasks managed through the MCP server. Currently, the system provides excellent programmatic access through MCP tools, but lacks a human-friendly interface for direct viewing and interaction.

## Current State Analysis

### Existing Capabilities
- MCP server with FastMCP framework
- SQLite database with projects and tasks tables
- Complete CRUD operations via MCP tools:
  - `list_projects()` - Returns project summaries
  - `get_project(project_id)` - Returns detailed project with tasks
  - `get_project_stats()` - Returns overall statistics
  - Task management tools for status updates

### Data Models
- **Project**: ID, name, description, timestamps, task collection
- **Task**: ID, description, category, status (backlog/in_progress/review/complete), timestamps
- **Task Statistics**: Counts by status within each project

## Technical Requirements

### Architecture
- **Backend**: Extend existing FastMCP server to serve both MCP tools and HTTP endpoints
- **Frontend**: Lightweight web interface using modern HTML/CSS/JavaScript
- **Database**: Continue using existing SQLite database (no schema changes needed)
- **Deployment**: Single-file deployment maintaining current simplicity

### Technology Stack
- **Backend Framework**: FastAPI (FastMCP is built on FastAPI)
- **Frontend**: Vanilla JavaScript with modern CSS (avoid complex frameworks)
- **Templating**: Jinja2 templates for server-side rendering
- **Styling**: CSS with modern features (Grid, Flexbox, CSS variables)

## User Interface Design

### Layout Structure
```
Header: Project Tracker Dashboard
├── Navigation: Projects | Stats | Help
└── Main Content Area
    ├── Project List View (default)
    │   ├── Project Cards with summary info
    │   └── Task count indicators
    └── Project Detail View
        ├── Project info header
        ├── Task statistics dashboard
        └── Task list with filtering
```

### Views Specification

#### 1. Dashboard View (`/`)
- **Purpose**: Overview of all projects with quick access
- **Components**:
  - Summary statistics panel (total projects, tasks, completion rates)
  - Project list with cards showing:
    - Project name and description
    - Task count by status (badges/indicators)
    - Last updated timestamp
    - Quick action buttons (View Details, Archive)
- **Interactions**:
  - Click project card → Navigate to project detail
  - Search/filter projects by name

#### 2. Project Detail View (`/project/{project_id}`)
- **Purpose**: Detailed view of single project with all tasks
- **Components**:
  - Project header with name, description, metadata
  - Task statistics visualization (progress bar, status counts)
  - Task list with columns:
    - Description
    - Category (with color coding)
    - Status (with visual indicators)
    - Timestamps
    - Actions (Change Status)
- **Interactions**:
  - Filter tasks by status or category
  - Sort tasks by date, status, category
  - Update task status via dropdown
  - Mark multiple tasks for batch operations

#### 3. Statistics View (`/stats`)
- **Purpose**: System-wide analytics and insights
- **Components**:
  - Overall project and task metrics
  - Completion trends over time
  - Category distribution charts
  - Project activity timeline

### Visual Design System

#### Color Scheme
```css
:root {
  --primary: #2563eb;      /* Blue for primary actions */
  --success: #16a34a;      /* Green for completed tasks */
  --warning: #d97706;      /* Orange for in-progress */
  --info: #0891b2;         /* Cyan for review */
  --neutral: #6b7280;      /* Gray for backlog */
  --background: #f8fafc;   /* Light gray background */
  --surface: #ffffff;      /* White cards/surfaces */
  --text: #1f2937;         /* Dark gray text */
  --border: #e5e7eb;       /* Light border color */
}
```

#### Task Status Indicators
- **Backlog**: Gray dot/badge
- **In Progress**: Orange dot/badge with pulse animation
- **Review**: Blue dot/badge
- **Complete**: Green dot/badge with checkmark

#### Typography
- Headers: Sans-serif, bold
- Body: Sans-serif, regular
- Monospace: Code/IDs
- Icon font: Simple icons for status, actions

## API Endpoints Design

### HTTP Routes (in addition to MCP tools)
```python
GET  /                           # Dashboard view
GET  /project/{project_id}       # Project detail view
GET  /stats                      # Statistics view
GET  /api/projects               # JSON API for projects
GET  /api/project/{project_id}   # JSON API for project details
PUT  /api/task/{task_id}/status  # Update task status
POST /api/project/{project_id}/tasks  # Create new task
```

### Response Formats
All API endpoints return JSON with consistent structure:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

Error responses:
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Implementation Plan

### Phase 1: Backend Extensions
1. **HTTP Server Integration**
   - Extend FastMCP server to include FastAPI HTTP routes
   - Add static file serving for CSS/JS/images
   - Add template rendering with Jinja2

2. **API Endpoints**
   - Create REST endpoints that wrap existing MCP tools
   - Add CORS support for development
   - Implement proper error handling and status codes

3. **Template System**
   - Set up Jinja2 templating
   - Create base template with common layout
   - Design responsive CSS framework

### Phase 2: Frontend Implementation
1. **Dashboard Page**
   - Project list with cards
   - Statistics summary
   - Search and filter functionality

2. **Project Detail Page**
   - Task list with interactive status updates
   - Task filtering and sorting
   - Progress visualization

3. **Interactive Features**
   - AJAX forms for status updates
   - Real-time updates (optional WebSocket)
   - Responsive design for mobile

### Phase 3: Enhancement Features
1. **Advanced Interactions**
   - Drag-and-drop task status updates
   - Bulk task operations
   - Task creation forms

2. **Data Visualization**
   - Progress charts
   - Timeline views
   - Category analytics

3. **User Experience**
   - Keyboard shortcuts
   - Toast notifications
   - Loading states and animations

## File Structure
```
project-tracking-mcp/
├── server.py                 # Enhanced server with HTTP routes
├── models.py                 # Existing models (no changes)
├── database.py               # Existing database (no changes)
├── templates/                # Jinja2 templates
│   ├── base.html
│   ├── dashboard.html
│   ├── project_detail.html
│   └── stats.html
├── static/                   # Static assets
│   ├── css/
│   │   ├── main.css
│   │   └── components.css
│   ├── js/
│   │   ├── main.js
│   │   ├── dashboard.js
│   │   └── project.js
│   └── images/
└── web_routes.py            # HTTP route handlers
```

## Security Considerations
- Input validation on all form submissions
- CSRF protection for state-changing operations
- Rate limiting on API endpoints
- Sanitize user inputs in templates
- No authentication required (single-user desktop application)

## Performance Requirements
- Dashboard load time: < 500ms for 100 projects
- Task list rendering: < 200ms for 500 tasks
- Status updates: < 100ms response time
- Mobile responsive design
- Progressive enhancement (works without JavaScript)

## Backwards Compatibility
- All existing MCP tools remain unchanged
- Database schema stays the same
- Server can run in MCP-only mode with flag
- Web interface is additive, not replacing MCP functionality

## Testing Strategy
- Unit tests for new HTTP endpoints
- Integration tests for template rendering
- End-to-end tests for critical user flows
- Performance testing with large datasets
- Cross-browser compatibility testing

## Deployment Options
1. **Development**: Run with auto-reload for development
2. **Desktop**: Single executable with embedded web server
3. **Network**: Bind to network interface for team access
4. **Docker**: Container deployment option

## Success Metrics
- User can view all projects within 2 clicks
- Task status updates are intuitive and fast
- Interface works well on desktop and mobile
- No performance degradation to existing MCP tools
- Maintains single-file database simplicity