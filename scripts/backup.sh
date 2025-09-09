#!/bin/bash

# Backup script for English with Toto Django application
# Usage: ./scripts/backup.sh [environment]

set -e

# Configuration
ENVIRONMENT=${1:-staging}
PROJECT_NAME="english-with-toto"
BACKUP_DIR="/opt/backups/$PROJECT_NAME"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$ENVIRONMENT_$DATE.tar.gz"

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

log "Starting backup for $ENVIRONMENT environment"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

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

# Create temporary directory for backup
TEMP_DIR="/tmp/backup_$DATE"
mkdir -p "$TEMP_DIR"

# Backup database
log "Backing up database"
docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U "$DB_USER" "$DB_NAME" > "$TEMP_DIR/database.sql"

# Backup media files
log "Backing up media files"
if [ -d "media" ]; then
    cp -r media "$TEMP_DIR/"
fi

# Backup static files
log "Backing up static files"
if [ -d "static" ]; then
    cp -r static "$TEMP_DIR/"
fi

# Backup environment configuration
log "Backing up environment configuration"
cp "$ENV_FILE" "$TEMP_DIR/"

# Create backup archive
log "Creating backup archive"
tar -czf "$BACKUP_FILE" -C "$TEMP_DIR" .

# Clean up temporary directory
rm -rf "$TEMP_DIR"

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "Backup created successfully: $BACKUP_FILE ($BACKUP_SIZE)"
else
    error "Backup creation failed"
fi

# Clean up old backups (keep last 7 days)
log "Cleaning up old backups"
find "$BACKUP_DIR" -name "backup_${ENVIRONMENT}_*.tar.gz" -mtime +7 -delete

log "Backup completed successfully!"
