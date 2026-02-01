# FastAPI Todo Application

A simple RESTful API for managing todos built with FastAPI and SQLAlchemy.

## Features

- Create, read, update, and delete todos
- SQLite database for data persistence
- Field validation with Pydantic
- RESTful API design

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) - Python package installer

## Installation

### 1. Install uv

If you haven't installed `uv` yet, install it using:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the repository

```bash
cd /path/to/your/workspace
```

### 3. Install dependencies

```bash
# uv will automatically create a virtual environment and install dependencies
uv sync
```

## Running the Application

### Start the development server

```bash
uv run fastapi dev main.py
```

The API will be available at `http://localhost:8000`

### Start the production server

```bash
uv run fastapi run main.py
```

## API Documentation

Once the server is running, you can access:

- **Interactive API documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative API documentation (ReDoc)**: http://localhost:8000/redoc

## Database

The application uses SQLite with a database file `todos.db` created automatically on first run.

### Database Schema

**Todos Table:**
- `id`: Integer (Primary Key)
- `title`: String
- `description`: String
- `priority`: Integer
- `completed`: Boolean

### Inspecting the database

You can inspect the database using the SQLite command-line tool:

```bash
sqlite3 todos.db
```

Example queries:
```sql
-- List all todos
SELECT * FROM todos;

-- Count todos
SELECT COUNT(*) FROM todos;

-- Exit
.exit
```

## Project Structure

```
todoapp/
├── main.py          # FastAPI application and endpoints
├── models.py        # SQLAlchemy models
├── database.py      # Database configuration
├── pyproject.toml   # Project metadata and dependencies
├── README.md        # This file
└── todos.db         # SQLite database (created on first run)
```

## Development

### Adding new dependencies

```bash
# Add a new dependency
uv add package-name
```

### Reinstalling dependencies

```bash
uv sync
```

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type hints
- **SQLite**: Lightweight database
- **uvicorn**: ASGI server (included with fastapi[standard])
