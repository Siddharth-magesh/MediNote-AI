# MediNote-AI Production Deployment Guide

This guide covers deploying MediNote-AI to a production environment.

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Docker 24.0+ and Docker Compose 2.0+
- Domain name with DNS configured
- At least 4GB RAM, 2 CPU cores, 50GB storage
- Google Cloud account (for Speech-to-Text)
- Groq API key (for AI extraction)

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/medinote-ai.git
cd medinote-ai

# 2. Copy and configure environment
cp .env.production.example .env.production
nano .env.production  # Edit with your values

# 3. Create required directories
mkdir -p nginx/ssl credentials

# 4. Add Google Cloud credentials
cp /path/to/google-credentials.json credentials/

# 5. Initialize SSL certificates
chmod +x scripts/ssl/init-letsencrypt.sh
./scripts/ssl/init-letsencrypt.sh your-domain.com your-email@example.com

# 6. Start all services
docker-compose -f docker-compose.prod.yml up -d

# 7. Run database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 8. Create initial admin user
docker-compose -f docker-compose.prod.yml exec backend python scripts/create_admin.py
```

## Detailed Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for docker group
```

### 2. Environment Configuration

Edit `.env.production` with secure values:

```bash
# Generate secure secrets
openssl rand -hex 32  # For JWT_SECRET_KEY
openssl rand -hex 32  # For JWT_REFRESH_SECRET_KEY
openssl rand -base64 24  # For POSTGRES_PASSWORD
```

### 3. SSL Certificates

For production, use Let's Encrypt:

```bash
# First time setup (uses staging by default for testing)
./scripts/ssl/init-letsencrypt.sh medinote.example.com admin@example.com 1

# When ready for production certificates
./scripts/ssl/init-letsencrypt.sh medinote.example.com admin@example.com 0
```

### 4. Database Setup

```bash
# Start only the database first
docker-compose -f docker-compose.prod.yml up -d postgres

# Wait for it to be ready
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 5. Start All Services

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | https://medinote.example.com | Main application |
| API | https://medinote.example.com/api | Backend API |
| Grafana | https://medinote.example.com/grafana | Monitoring dashboard |
| MinIO Console | http://server-ip:9001 | Object storage (internal only) |

## Monitoring & Alerts

### Grafana Dashboard

Access Grafana at `https://your-domain/grafana`:

1. Login with credentials from `.env.production`
2. Navigate to MediNote-AI dashboards
3. Set up alert notifications (Email, Slack, etc.)

### Key Metrics to Monitor

- **API Response Time**: p95 should be < 500ms
- **Error Rate**: Should be < 1%
- **Database Connections**: Should be < 80% of max
- **Memory Usage**: Should be < 80%
- **Disk Space**: Should be > 20% free

### Setting Up Alerts

Configure Alertmanager for notifications:

```yaml
# monitoring/alertmanager/alertmanager.yml
route:
  receiver: 'email-notifications'

receivers:
  - name: 'email-notifications'
    email_configs:
      - to: 'admin@example.com'
        from: 'alerts@medinote.example.com'
        smarthost: 'smtp.example.com:587'
```

## Backup & Recovery

### Automated Backups

Backups are configured to run daily at 2 AM:

```bash
# View backup crontab
docker-compose -f docker-compose.prod.yml exec backup crontab -l

# Trigger manual backup
docker-compose -f docker-compose.prod.yml exec backup /scripts/backup.sh
```

### Restore from Backup

```bash
# List available backups
docker-compose -f docker-compose.prod.yml exec backup ls -la /backups

# Restore specific backup
docker-compose -f docker-compose.prod.yml exec backup /scripts/restore.sh /backups/medinote_20240215_020000.sql.gz
```

### Off-site Backup

Configure S3/MinIO backup replication:

```bash
# Install MinIO client
docker-compose -f docker-compose.prod.yml exec minio mc alias set remote https://s3.amazonaws.com ACCESS_KEY SECRET_KEY

# Mirror backup bucket
docker-compose -f docker-compose.prod.yml exec minio mc mirror /data/backups remote/medinote-backups
```

## Scaling

### Horizontal Scaling

For high-traffic deployments:

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "2"
          memory: 2G
```

### Database Read Replicas

For read-heavy workloads, add PostgreSQL replicas:

```yaml
services:
  postgres-replica:
    image: postgres:15-alpine
    environment:
      POSTGRES_HOST: postgres
      POSTGRES_REPLICATION: "true"
```

## Security Checklist

- [ ] Changed all default passwords
- [ ] SSL/TLS configured with A+ rating
- [ ] Firewall configured (only 80, 443 open)
- [ ] SSH key authentication only
- [ ] Regular security updates enabled
- [ ] Backup encryption enabled
- [ ] Access logs monitored
- [ ] Rate limiting configured
- [ ] CORS properly configured

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Check container status
docker-compose -f docker-compose.prod.yml ps

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Check connection from backend
docker-compose -f docker-compose.prod.yml exec backend python -c "from app.db.session import engine; print(engine)"
```

### SSL Certificate Issues

```bash
# Check certificate status
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Renew certificates manually
docker-compose -f docker-compose.prod.yml run --rm certbot renew
```

### High Memory Usage

```bash
# Check container memory
docker stats

# Restart memory-hungry containers
docker-compose -f docker-compose.prod.yml restart backend
```

## Maintenance

### Regular Updates

```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Clean old images
docker image prune -f
```

### Log Rotation

Logs are automatically rotated by Docker. Configure in daemon.json:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### Health Checks

All services have health checks configured. Monitor at:

```bash
# Overall health
curl https://your-domain.com/health

# Individual services
docker-compose -f docker-compose.prod.yml exec backend curl http://localhost:8000/health
```

## Support

For issues or questions:

1. Check logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Review documentation: `/docs` folder
3. Open an issue: https://github.com/your-org/medinote-ai/issues
