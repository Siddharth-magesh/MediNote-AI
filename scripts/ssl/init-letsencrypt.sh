#!/bin/bash
# Initialize Let's Encrypt SSL certificates for MediNote-AI
# Usage: ./init-letsencrypt.sh your-domain.com your-email@example.com

set -e

# Configuration
DOMAIN=${1:-medinote.example.com}
EMAIL=${2:-admin@example.com}
STAGING=${3:-0}  # Set to 1 for testing with Let's Encrypt staging

COMPOSE_FILE="docker-compose.prod.yml"
DATA_PATH="./certbot"

echo "=== MediNote-AI SSL Certificate Setup ==="
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo "Staging: $STAGING"
echo ""

# Check if certificates already exist
if [ -d "$DATA_PATH/conf/live/$DOMAIN" ]; then
    read -p "Existing certificates found. Do you want to replace them? (y/N) " decision
    if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
        echo "Keeping existing certificates."
        exit 0
    fi
fi

# Create required directories
echo "Creating certificate directories..."
mkdir -p "$DATA_PATH/conf/live/$DOMAIN"
mkdir -p "$DATA_PATH/www"

# Download recommended TLS parameters
if [ ! -e "$DATA_PATH/conf/options-ssl-nginx.conf" ]; then
    echo "Downloading recommended TLS parameters..."
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$DATA_PATH/conf/options-ssl-nginx.conf"
fi

if [ ! -e "$DATA_PATH/conf/ssl-dhparams.pem" ]; then
    echo "Downloading DH parameters..."
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$DATA_PATH/conf/ssl-dhparams.pem"
fi

# Create dummy certificate for nginx to start
echo "Creating dummy certificate for $DOMAIN..."
openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
    -keyout "$DATA_PATH/conf/live/$DOMAIN/privkey.pem" \
    -out "$DATA_PATH/conf/live/$DOMAIN/fullchain.pem" \
    -subj "/CN=$DOMAIN"

# Start nginx with dummy certificate
echo "Starting nginx..."
docker-compose -f $COMPOSE_FILE up -d nginx

# Wait for nginx to start
echo "Waiting for nginx to start..."
sleep 5

# Delete dummy certificate
echo "Deleting dummy certificate..."
rm -rf "$DATA_PATH/conf/live/$DOMAIN"

# Request Let's Encrypt certificate
echo "Requesting Let's Encrypt certificate for $DOMAIN..."

# Set staging flag
STAGING_ARG=""
if [ $STAGING != "0" ]; then
    STAGING_ARG="--staging"
fi

docker-compose -f $COMPOSE_FILE run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
    $STAGING_ARG \
    --email $EMAIL \
    --rsa-key-size 4096 \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d $DOMAIN \
    -d www.$DOMAIN" certbot

echo "Reloading nginx..."
docker-compose -f $COMPOSE_FILE exec nginx nginx -s reload

echo ""
echo "=== SSL Certificate Setup Complete ==="
echo ""
echo "Your SSL certificates have been obtained and configured."
echo ""
echo "Next steps:"
echo "1. Update nginx/conf.d/default.conf with your domain"
echo "2. Uncomment the HSTS header after confirming HTTPS works"
echo "3. Set up automatic renewal with cron:"
echo "   0 0 * * * cd /path/to/medinote && docker-compose -f docker-compose.prod.yml run --rm certbot renew && docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload"
