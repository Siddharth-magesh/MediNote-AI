#!/bin/bash
# MediNote-AI Database Backup Script
# Creates compressed PostgreSQL backups with rotation

set -e

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=${RETENTION_DAYS:-30}
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/medinote_${TIMESTAMP}.sql.gz"

# Database connection (from environment)
DB_HOST=${POSTGRES_HOST:-postgres}
DB_NAME=${POSTGRES_DB:-medinote}
DB_USER=${POSTGRES_USER:-medinote}

echo "=== MediNote-AI Database Backup ==="
echo "Timestamp: $TIMESTAMP"
echo "Database: $DB_NAME"
echo "Backup file: $BACKUP_FILE"
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup
echo "Creating backup..."
pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
    --format=custom \
    --compress=9 \
    --verbose \
    --file="$BACKUP_FILE.tmp"

# Move to final location (atomic operation)
mv "$BACKUP_FILE.tmp" "$BACKUP_FILE"

# Verify backup
echo "Verifying backup..."
BACKUP_SIZE=$(stat -c%s "$BACKUP_FILE")
if [ "$BACKUP_SIZE" -lt 1000 ]; then
    echo "ERROR: Backup file is suspiciously small ($BACKUP_SIZE bytes)"
    exit 1
fi

echo "Backup created successfully: $BACKUP_FILE ($BACKUP_SIZE bytes)"

# Cleanup old backups
echo ""
echo "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "medinote_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

# List current backups
echo ""
echo "Current backups:"
ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null || echo "No backups found"

echo ""
echo "=== Backup Complete ==="
