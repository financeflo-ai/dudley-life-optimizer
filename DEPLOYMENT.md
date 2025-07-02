# Dudley Life Optimizer - Deployment Guide

This guide provides step-by-step instructions for deploying the Dudley Life Optimizer platform in various environments.

## 🚀 Quick Start Deployment

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account
- OpenAI API key
- Anthropic API key
- GitHub account (for repository access)

### 1. Clone Repository
```bash
git clone https://github.com/financeflo-ai/dudley-life-optimizer.git
cd dudley-life-optimizer
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

### 3. Configure Environment Variables
Edit `.env` file with your credentials:
```bash
# Database Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# AI Service APIs
OPENAI_API_KEY=sk-your_openai_key
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key

# Security Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here
MFA_ISSUER=Dudley Life Optimizer

# Application Settings
FLASK_ENV=production
FLASK_DEBUG=False
CORS_ORIGINS=https://your-frontend-domain.com

# Optional: Email & SMS
SENDGRID_API_KEY=your_sendgrid_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
```

### 4. Initialize Database
```bash
# Run database initialization script
python scripts/init_database.py

# Apply database schema
python scripts/apply_schema.py
```

### 5. Start Backend Server
```bash
# Development
python src/main.py

# Production with Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 src.main:app
```

### 6. Frontend Setup (Optional)
```bash
# Navigate to frontend directory
cd ../dudley_life_optimizer_frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your backend API URL

# Build for production
npm run build

# Serve static files (or deploy to CDN)
npm run preview
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Clone repository
git clone https://github.com/financeflo-ai/dudley-life-optimizer.git
cd dudley-life-optimizer

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Manual Docker Build
```bash
# Build backend image
docker build -t dudley-life-optimizer-backend .

# Run backend container
docker run -d \
  --name dudley-backend \
  -p 8000:8000 \
  --env-file .env \
  dudley-life-optimizer-backend

# Build frontend image (if using)
cd frontend
docker build -t dudley-life-optimizer-frontend .

# Run frontend container
docker run -d \
  --name dudley-frontend \
  -p 3000:3000 \
  dudley-life-optimizer-frontend
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS
```bash
# Install AWS CLI and configure credentials
aws configure

# Create ECS cluster
aws ecs create-cluster --cluster-name dudley-life-optimizer

# Build and push to ECR
aws ecr create-repository --repository-name dudley-life-optimizer
docker build -t dudley-life-optimizer .
docker tag dudley-life-optimizer:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/dudley-life-optimizer:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/dudley-life-optimizer:latest

# Deploy using ECS task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
aws ecs create-service --cluster dudley-life-optimizer --service-name dudley-service --task-definition dudley-task
```

#### Using AWS Lambda (Serverless)
```bash
# Install Serverless Framework
npm install -g serverless

# Deploy serverless backend
serverless deploy --stage production

# Configure API Gateway and Lambda functions
# (See serverless.yml configuration)
```

### Google Cloud Platform

#### Using Cloud Run
```bash
# Install gcloud CLI and authenticate
gcloud auth login
gcloud config set project your-project-id

# Build and deploy
gcloud builds submit --tag gcr.io/your-project-id/dudley-life-optimizer
gcloud run deploy dudley-life-optimizer \
  --image gcr.io/your-project-id/dudley-life-optimizer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Using Google Kubernetes Engine (GKE)
```bash
# Create GKE cluster
gcloud container clusters create dudley-cluster \
  --num-nodes=3 \
  --zone=us-central1-a

# Deploy using Kubernetes manifests
kubectl apply -f k8s/
```

### Microsoft Azure

#### Using Azure Container Instances
```bash
# Install Azure CLI and login
az login

# Create resource group
az group create --name dudley-rg --location eastus

# Deploy container
az container create \
  --resource-group dudley-rg \
  --name dudley-life-optimizer \
  --image your-registry/dudley-life-optimizer:latest \
  --dns-name-label dudley-app \
  --ports 8000
```

## 🔧 Production Configuration

### Environment-Specific Settings

#### Production (.env.production)
```bash
FLASK_ENV=production
FLASK_DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=https://app.dudley-life-optimizer.com
DATABASE_POOL_SIZE=20
REDIS_URL=redis://your-redis-instance:6379
CELERY_BROKER_URL=redis://your-redis-instance:6379
```

#### Staging (.env.staging)
```bash
FLASK_ENV=staging
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
CORS_ORIGINS=https://staging.dudley-life-optimizer.com
DATABASE_POOL_SIZE=10
```

#### Development (.env.development)
```bash
FLASK_ENV=development
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
DATABASE_POOL_SIZE=5
```

### Security Hardening

#### SSL/TLS Configuration
```bash
# Generate SSL certificates (Let's Encrypt)
certbot certonly --webroot -w /var/www/html -d your-domain.com

# Configure Nginx with SSL
# (See nginx.conf.example)
```

#### Firewall Configuration
```bash
# UFW (Ubuntu)
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable

# iptables
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP
```

### Database Configuration

#### Supabase Production Setup
```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Create database schema
\i database_schema.sql

-- Set up Row Level Security policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_metrics ENABLE ROW LEVEL SECURITY;
-- (Continue for all tables)

-- Create indexes for performance
CREATE INDEX idx_journal_entries_user_id ON journal_entries(user_id);
CREATE INDEX idx_journal_entries_created_at ON journal_entries(created_at);
CREATE INDEX idx_health_metrics_user_id ON health_metrics(user_id);
CREATE INDEX idx_health_metrics_recorded_at ON health_metrics(recorded_at);
```

#### Backup Configuration
```bash
# Automated daily backups
crontab -e
# Add: 0 2 * * * /usr/local/bin/backup_database.sh

# Backup script example
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > /backups/dudley_db_$DATE.sql
aws s3 cp /backups/dudley_db_$DATE.sql s3://your-backup-bucket/
```

## 📊 Monitoring & Logging

### Application Monitoring
```bash
# Install monitoring tools
pip install prometheus-client sentry-sdk

# Configure Prometheus metrics endpoint
# (See monitoring/prometheus.py)

# Set up Grafana dashboard
# (Import dashboard from monitoring/grafana-dashboard.json)
```

### Log Management
```bash
# Configure structured logging
# (See src/utils/logging.py)

# Set up log rotation
sudo nano /etc/logrotate.d/dudley-life-optimizer
```

### Health Checks
```bash
# Application health endpoint
curl http://localhost:8000/health

# Database connectivity check
curl http://localhost:8000/health/database

# AI services check
curl http://localhost:8000/health/ai-services
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy Dudley Life Optimizer

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Your deployment commands here
```

### Automated Testing
```bash
# Run full test suite
pytest tests/ --cov=src --cov-report=html

# Run security tests
bandit -r src/

# Run performance tests
locust -f tests/performance/locustfile.py
```

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check Supabase connection
python -c "from src.models.supabase_client import get_supabase_client; print(get_supabase_client().table('user_profiles').select('*').limit(1).execute())"

# Verify environment variables
env | grep SUPABASE
```

#### AI Service Issues
```bash
# Test OpenAI connection
python -c "import openai; openai.api_key='your-key'; print(openai.Model.list())"

# Test Anthropic connection
python -c "from anthropic import Anthropic; client = Anthropic(api_key='your-key'); print('Connected')"
```

#### Performance Issues
```bash
# Check system resources
htop
df -h
free -m

# Monitor application logs
tail -f logs/application.log

# Check database performance
# (Use Supabase dashboard or pg_stat_statements)
```

### Log Analysis
```bash
# Search for errors
grep -i error logs/application.log

# Monitor API response times
grep "response_time" logs/application.log | awk '{print $NF}' | sort -n

# Check authentication failures
grep "authentication_failed" logs/security.log
```

## 📞 Support & Maintenance

### Regular Maintenance Tasks
```bash
# Weekly database maintenance
python scripts/maintenance/cleanup_old_data.py
python scripts/maintenance/optimize_database.py

# Monthly security updates
pip list --outdated
npm audit
```

### Backup Verification
```bash
# Test backup restoration
python scripts/test_backup_restore.py

# Verify backup integrity
python scripts/verify_backup_integrity.py
```

### Performance Optimization
```bash
# Database query optimization
python scripts/analyze_slow_queries.py

# Application profiling
python -m cProfile -o profile.stats src/main.py
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] Database schema applied
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Backup system tested
- [ ] Monitoring tools configured

### Post-Deployment
- [ ] Health checks passing
- [ ] Authentication working
- [ ] AI services responding
- [ ] Database connections stable
- [ ] Logs being generated
- [ ] Monitoring alerts configured

### Security Verification
- [ ] MFA working correctly
- [ ] Data encryption verified
- [ ] Audit logs capturing events
- [ ] Rate limiting active
- [ ] CORS properly configured
- [ ] Security headers present

---

For additional support or questions about deployment, please refer to the main README.md or contact the development team.

