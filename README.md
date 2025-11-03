# adk-triage-agent

An intelligent triage agent built with Google ADK and GenAI.

## Project Structure

```
adk-triage-agent/
│
├── src/                    # Source code
│   ├── __init__.py
│   └── main.py            # Main entry point
│
├── tests/                  # Unit tests
│   ├── __init__.py
│   └── test_main.py
│
├── docs/                   # Documentation
│   └── README.md
│
├── adk_env/               # Virtual environment (not in git)
│
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore file
├── requirements.txt       # Project dependencies
├── requirements-dev.txt   # Development dependencies
├── agent.py               # Legacy file (to be removed)
└── README.md              # This file
```

## Setup Instructions

### 1. Create and Activate Virtual Environment

```powershell
# Create virtual environment
python -m venv adk_env

# Activate the environment
.\adk_env\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
# Install main dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 3. Configure Environment Variables

```powershell
# Copy the example environment file
copy .env.example .env

# Edit .env and add your Google API key
```

### 4. Run the Agent

```powershell
python src/main.py
```

### 5. Run Tests

```powershell
pytest
```

## Requirements

**Main Dependencies** (`requirements.txt`):
- google-adk
- google-genai

**Development Dependencies** (`requirements-dev.txt`):
- pytest (testing framework)
- pytest-cov (code coverage)
- black (code formatter)
- flake8 (linter)
- mypy (type checker)
- python-dotenv (environment variable management)

## Development

### Code Formatting
```powershell
black src/ tests/
```

### Linting
```powershell
flake8 src/ tests/
```

### Type Checking
```powershell
mypy src/
```

## Contributing

1. Follow PEP 8 style guidelines
2. Write tests for new features
3. Run tests before committing
4. Use meaningful commit messages