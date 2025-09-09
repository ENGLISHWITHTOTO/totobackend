#!/bin/bash

# Deployment script for English with Toto Django application
# Usage: ./scripts/deploy.sh [environment] [version]

set -e

# Configuration
ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}
PROJECT_NAME="english-with-toto"
DOCKER_IMAGE="english-with-toto/backend"
DEPLOY_DIR="/opt/$PROJECT_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root"
fi

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    error "Environment must be 'staging' or 'production'"
fi

log "Starting deployment for $ENVIRONMENT environment with version $VERSION"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    error "Docker is not running or not accessible"
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    error "docker-compose is not installed"
fi

# Create deployment directory if it doesn't exist
if [ ! -d "$DEPLOY_DIR" ]; then
    log "Creating deployment directory: $DEPLOY_DIR"
    sudo mkdir -p "$DEPLOY_DIR"
    sudo chown $USER:$USER "$DEPLOY_DIR"
fi

# Navigate to deployment directory
cd "$DEPLOY_DIR"

# Pull latest code
log "Pulling latest code from repository"
git pull origin main

# Set environment-specific variables
if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILE="docker-compose.production.yml"
    ENV_FILE=".env.production"
    IMAGE_TAG="latest"
else
    COMPOSE_FILE="docker-compose.staging.yml"
    ENV_FILE=".env.staging"
    IMAGE_TAG="develop"
fi

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    error "Environment file $ENV_FILE not found"
fi

# Pull Docker images
log "Pulling Docker images"
docker-compose -f "$COMPOSE_FILE" pull

# Stop existing containers
log "Stopping existing containers"
docker-compose -f "$COMPOSE_FILE" down

# Start new containers
log "Starting new containers"
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for services to be ready
log "Waiting for services to be ready"
sleep 30

# Run database migrations
log "Running database migrations"
docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py migrate

# Collect static files
log "Collecting static files"
docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py collectstatic --noinput

# Clear cache
log "Clearing cache"
docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py clear_cache

# Health check
log "Performing health check"
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    log "Health check passed"
else
    error "Health check failed"
fi

# Clean up old images
log "Cleaning up old Docker images"
docker image prune -f

log "Deployment completed successfully!"

# Show running containers
log "Running containers:"
docker-compose -f "$COMPOSE_FILE" ps
