# WebGen PowerShell Deployment Script

Write-Host "🚀 Starting WebGen deployment..." -ForegroundColor Blue

# Function to write colored output
function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Error-Custom "Docker is not running. Please start Docker and try again."
    exit 1
}

# Check if Docker Compose is available
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Error-Custom "Docker Compose is not installed. Please install it and try again."
    exit 1
}

# Create data directories
Write-Info "Creating data directories..."
New-Item -ItemType Directory -Force -Path "data\scraped_data", "data\output", "data\debug" | Out-Null
Write-Success "Data directories created"

# Build and start the application
Write-Info "Building and starting WebGen application..."
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# Wait for the application to start
Write-Info "Waiting for application to be healthy..."
Start-Sleep -Seconds 10

# Check if the application is healthy
$attempts = 0
$maxAttempts = 30

while ($attempts -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "WebGen is running and healthy!"
            Write-Host ""
            Write-Host "🌟 Deployment completed successfully!" -ForegroundColor Magenta
            Write-Host ""
            Write-Host "📱 Application is available at: http://localhost:5000" -ForegroundColor White
            Write-Host "🔍 API Health check: http://localhost:5000/api/health" -ForegroundColor White
            Write-Host ""
            Write-Host "🐳 Docker commands:" -ForegroundColor White
            Write-Host "  View logs: docker-compose logs -f" -ForegroundColor Gray
            Write-Host "  Stop app:  docker-compose down" -ForegroundColor Gray
            Write-Host "  Restart:   docker-compose restart" -ForegroundColor Gray
            Write-Host ""
            exit 0
        }
    } catch {
        # Continue checking
    }
    
    Write-Host -NoNewline "."
    Start-Sleep -Seconds 2
    $attempts++
}

Write-Error-Custom "Application failed to start properly. Check the logs with 'docker-compose logs'"
exit 1
