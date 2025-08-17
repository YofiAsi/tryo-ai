#!/bin/bash

# Docker Build and Run Script for HR Backend API
# This script builds and runs the Docker containers for the HR Backend API

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Function to build and run
build_and_run() {
    print_status "Building Docker images..."
    docker-compose build --no-cache
    
    print_status "Starting services..."
    docker-compose up -d
    
    print_status "Waiting for services to be healthy..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_status "All services are running successfully!"
        print_status "API is available at: http://localhost:8000"
        print_status "API Documentation: http://localhost:8000/docs"
        print_status "MongoDB: localhost:27017"
        print_status "Redis: localhost:6379"
    else
        print_error "Some services failed to start. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose down
    print_status "Services stopped."
}

# Function to show logs
show_logs() {
    print_status "Showing logs..."
    docker-compose logs -f
}

# Function to show status
show_status() {
    print_status "Service status:"
    docker-compose ps
}

# Function to clean up
cleanup() {
    print_warning "This will remove all containers, networks, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        print_status "Cleanup completed."
    else
        print_status "Cleanup cancelled."
    fi
}

# Main script logic
case "${1:-}" in
    "build")
        print_status "Building Docker images..."
        docker-compose build --no-cache
        ;;
    "run")
        build_and_run
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 2
        build_and_run
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  build     Build Docker images"
        echo "  run       Build and run services (default)"
        echo "  stop      Stop all services"
        echo "  restart   Restart all services"
        echo "  logs      Show logs from all services"
        echo "  status    Show status of all services"
        echo "  cleanup   Remove all containers, networks, and volumes"
        echo "  help      Show this help message"
        ;;
    *)
        build_and_run
        ;;
esac
