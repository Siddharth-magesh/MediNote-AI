#!/bin/bash
# MediNote-AI Database Restore Script
# Restores PostgreSQL database from backup

set -e

# Configuration
BACKUP_DIR="/backups"

# Database connection (from environment)
DB_HOST=${POSTGRES_HOST:-postgres}
DB_NAME=${POSTGRES_DB:-medinote}
DB_USER=${POSTGRES_USER:-medinote}

# Get backup file from argument or list available
BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "=== Available Backups ==="
    ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null || echo "No backups found"
    echo ""
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 /backups/medinote_20240215_120000.sql.gz"
    exit 1
fi

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "=== MediNote-AI Database Restore ==="
echo "Backup file: $BACKUP_FILE"
echo "Target database: $DB_NAME"
echo ""

# Confirmation
read -p "WARNING: This will overwrite the current database. Continue? (yes/no) " confirm
if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Terminate existing connections
echo "Terminating existing database connections..."
psql -h "$DB_HOST" -U "$DB_USER" -d postgres -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '$DB_NAME'
AND pid <> pg_backend_pid();"

# Drop and recreate database
echo "Recreating database..."
psql -h "$DB_HOST" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
psql -h "$DB_HOST" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Restore from backup
echo "Restoring from backup..."
pg_restore -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
    --verbose \
    --no-owner \
    --no-privileges \
    "$BACKUP_FILE"

echo ""
echo "=== Restore Complete ==="
echo "Database $DB_NAME has been restored from $BACKUP_FILE"
