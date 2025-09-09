#!/bin/bash

# Restore script for English with Toto Django application
# Usage: ./scripts/restore.sh [environment] [backup_file]

set -e

# Configuration
ENVIRONMENT=${1:-staging}
BACKUP_FILE=${2}
PROJECT_NAME="english-with-toto"
BACKUP_DIR="/opt/backups/$PROJECT_NAME"

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

# Check if backup file is provided
if [ -z "$BACKUP_FILE" ]; then
    error "Backup file must be provided"
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    error "Backup file not found: $BACKUP_FILE"
fi

log "Starting restore for $ENVIRONMENT environment from $BACKUP_FILE"

# Set environment-specific variables
if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILE="docker-compose.production.yml"
    ENV_FILE=".env.production"
else
    COMPOSE_FILE="docker-compose.staging.yml"
    ENV_FILE=".env.staging"
fi

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    error "Environment file $ENV_FILE not found"
fi

# Load environment variables
source "$ENV_FILE"

# Create temporary directory for restore
TEMP_DIR="/tmp/restore_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEMP_DIR"

# Extract backup
log "Extracting backup file"
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Stop services
log "Stopping services"
docker-compose -f "$COMPOSE_FILE" down

# Restore database
log "Restoring database"
docker-compose -f "$COMPOSE_FILE" up -d db
sleep 10
docker-compose -f "$COMPOSE_FILE" exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker-compose -f "$COMPOSE_FILE" exec -T db psql -U "$DB_USER" -d "$DB_NAME" < "$TEMP_DIR/database.sql"

# Restore media files
log "Restoring media files"
if [ -d "$TEMP_DIR/media" ]; then
    rm -rf media
    cp -r "$TEMP_DIR/media" .
fi

# Restore static files
log "Restoring static files"
if [ -d "$TEMP_DIR/static" ]; then
    rm -rf static
    cp -r "$TEMP_DIR/static" .
fi

# Start all services
log "Starting all services"
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for services to be ready
log "Waiting for services to be ready"
sleep 30

# Run migrations
log "Running migrations"
docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py migrate

# Collect static files
log "Collecting static files"
docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py collectstatic --noinput

# Health check
log "Performing health check"
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    log "Health check passed"
else
    error "Health check failed"
fi

# Clean up temporary directory
rm -rf "$TEMP_DIR"

log "Restore completed successfully!"
