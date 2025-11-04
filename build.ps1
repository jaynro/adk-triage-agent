# Build and deployment helper script
# Usage: .\build.ps1 [command]

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host @"
ADK Triage Agent - Build Script

Commands:
  install       Install dependencies
  install-dev   Install with development dependencies
  install-prod  Install with production dependencies
  test          Run tests
  lint          Run linters
  format        Format code with black
  run-local     Run web server locally
  run-cli       Run CLI version
  docker-build  Build Docker image
  docker-run    Run Docker container locally
  deploy-gke    Deploy to Google Kubernetes Engine
  clean         Clean up temporary files
  help          Show this help message

Examples:
  .\build.ps1 install
  .\build.ps1 test
  .\build.ps1 deploy-gke
"@ -ForegroundColor Cyan
}

function Install-Dependencies {
    Write-Host "Installing dependencies..." -ForegroundColor Green
    pip install -r requirements.txt
}

function Install-DevDependencies {
    Write-Host "Installing development dependencies..." -ForegroundColor Green
    pip install -r requirements.txt -r requirements-dev.txt
}

function Install-ProdDependencies {
    Write-Host "Installing production dependencies..." -ForegroundColor Green
    pip install -r requirements.txt -r requirements-prod.txt
}

function Run-Tests {
    Write-Host "Running tests..." -ForegroundColor Green
    pytest
}

function Run-Lint {
    Write-Host "Running linters..." -ForegroundColor Green
    flake8 src/ tests/
    mypy src/
}

function Format-Code {
    Write-Host "Formatting code..." -ForegroundColor Green
    black src/ tests/
}

function Run-LocalServer {
    Write-Host "Starting web server..." -ForegroundColor Green
    python src/web_server.py
}

function Run-CLI {
    Write-Host "Starting CLI..." -ForegroundColor Green
    python src/main.py
}

function Build-DockerImage {
    Write-Host "Building Docker image..." -ForegroundColor Green
    docker build -t adk-triage-agent:latest .
}

function Run-DockerContainer {
    Write-Host "Running Docker container..." -ForegroundColor Green
    docker run -p 8080:8080 --env-file .env adk-triage-agent:latest
}

function Deploy-GKE {
    Write-Host "Deploying to GKE..." -ForegroundColor Green
    if ([string]::IsNullOrEmpty($env:GCP_PROJECT_ID)) {
        Write-Host "ERROR: GCP_PROJECT_ID not set" -ForegroundColor Red
        Write-Host "Set it with: `$env:GCP_PROJECT_ID = 'your-project-id'" -ForegroundColor Yellow
        exit 1
    }
    .\deploy-gke.ps1 -ProjectId $env:GCP_PROJECT_ID
}

function Clean-Up {
    Write-Host "Cleaning up..." -ForegroundColor Green
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue __pycache__
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .pytest_cache
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue src/__pycache__
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue tests/__pycache__
    Remove-Item -Force -ErrorAction SilentlyContinue .coverage
    Write-Host "Cleanup complete!" -ForegroundColor Green
}

# Execute command
switch ($Command.ToLower()) {
    "install" { Install-Dependencies }
    "install-dev" { Install-DevDependencies }
    "install-prod" { Install-ProdDependencies }
    "test" { Run-Tests }
    "lint" { Run-Lint }
    "format" { Format-Code }
    "run-local" { Run-LocalServer }
    "run-cli" { Run-CLI }
    "docker-build" { Build-DockerImage }
    "docker-run" { Run-DockerContainer }
    "deploy-gke" { Deploy-GKE }
    "clean" { Clean-Up }
    "help" { Show-Help }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
