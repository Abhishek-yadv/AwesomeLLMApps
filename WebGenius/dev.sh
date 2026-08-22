#!/bin/bash

# WebGen Development Helper Script

case "$1" in
    "install")
        echo "📦 Installing dependencies..."
        npm install
        npm run install-backend
        echo "✅ Dependencies installed!"
        ;;
    "dev")
        echo "🚀 Starting development servers..."
        echo "Starting backend..."
        npm run backend &
        sleep 5
        echo "Starting frontend..."
        npm run dev
        ;;
    "build")
        echo "🔨 Building application..."
        npm run build
        echo "✅ Build complete!"
        ;;
    "docker")
        echo "🐳 Starting Docker deployment..."
        docker-compose up --build
        ;;
    "docker-bg")
        echo "🐳 Starting Docker deployment in background..."
        docker-compose up --build -d
        ;;
    "clean")
        echo "🧹 Cleaning up..."
        docker-compose down
        docker system prune -f
        rm -rf node_modules .venv dist build
        echo "✅ Cleanup complete!"
        ;;
    "logs")
        echo "📋 Viewing Docker logs..."
        docker-compose logs -f
        ;;
    "status")
        echo "📊 Application Status:"
        echo "Frontend: http://localhost:5173 (dev) or http://localhost:5000 (prod)"
        echo "Backend:  http://localhost:5000"
        echo "API Docs: http://localhost:5000/docs"
        echo "Health:   http://localhost:5000/api/health"
        curl -s http://localhost:5000/api/health || echo "❌ Backend not responding"
        ;;
    *)
        echo "WebGen Development Helper"
        echo ""
        echo "Usage: ./dev.sh [command]"
        echo ""
        echo "Commands:"
        echo "  install    - Install all dependencies"
        echo "  dev        - Start development servers"
        echo "  build      - Build for production"
        echo "  docker     - Start with Docker Compose"
        echo "  docker-bg  - Start Docker in background"
        echo "  clean      - Clean up all files and containers"
        echo "  logs       - View Docker logs"
        echo "  status     - Check application status"
        ;;
esac
