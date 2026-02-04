#!/bin/bash
# Renew Let's Encrypt SSL certificates
# Add to crontab: 0 0 * * * /path/to/renew-certificates.sh >> /var/log/certbot-renew.log 2>&1

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"

echo "=== Certificate Renewal: $(date) ==="

cd "$PROJECT_DIR"

# Attempt to renew certificates
docker-compose -f $COMPOSE_FILE run --rm certbot renew --quiet

# Reload nginx to pick up new certificates
docker-compose -f $COMPOSE_FILE exec -T nginx nginx -s reload

echo "Certificate renewal completed successfully."
