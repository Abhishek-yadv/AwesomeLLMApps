#!/bin/bash

# WebGen Deployment Script
set -e  # Exit on any error

echo "🚀 Starting WebGen deployment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    log_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    log_error "Docker Compose is not installed. Please install it and try again."
    exit 1
fi

# Create data directories
log_info "Creating data directories..."
mkdir -p data/scraped_data data/output data/debug
log_success "Data directories created"

# Build and start the application
log_info "Building and starting WebGen application..."
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# Wait for the application to start
log_info "Waiting for application to be healthy..."
sleep 10

# Check if the application is healthy
for i in {1..30}; do
    if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
        log_success "WebGen is running and healthy!"
        echo ""
        echo "🌟 Deployment completed successfully!"
        echo ""
        echo "📱 Application is available at: http://localhost:5000"
        echo "🔍 API Health check: http://localhost:5000/api/health"
        echo ""
        echo "🐳 Docker commands:"
        echo "  View logs: docker-compose logs -f"
        echo "  Stop app:  docker-compose down"
        echo "  Restart:   docker-compose restart"
        echo ""
        exit 0
    fi
    echo -n "."
    sleep 2
done

log_error "Application failed to start properly. Check the logs with 'docker-compose logs'"
exit 1
