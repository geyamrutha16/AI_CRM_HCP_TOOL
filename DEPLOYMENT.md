# 🚀 Deployment Guide - AI-CRM HCP Module

Complete instructions for deploying the AI-CRM HCP application to production.

---

## 📋 Deployment Options

### 1. Traditional Server Setup

- Direct installation, full control
- Best for: Small to medium deployments, full customization
- See [Quick Setup](#traditional-deployment-local)

### 2. Platform as a Service (PaaS)

- Managed infrastructure, auto-scaling
- **Best for:** Startups, rapid deployment, minimal ops overhead
- Options: Railway, Render, AWS, Vercel, Netlify

---

## � Traditional Deployment (Local)

This is the native setup without containerization.

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your database and API keys

# Start server
python main.py
```

### Frontend Setup

```bash
cd frontend

# Install and build
npm install
npm run build

# Start dev server
npm run dev
# Or serve production build
npm install -g serve
serve -s dist -p 3000
```

---

## 🐳 Docker Deployment (Optional)

If you prefer containerization for easier deployment:

### Prerequisites

- Docker Desktop installed
- Docker Hub account (optional)

### Build Docker Images

```bash
# From project root
cd backend
docker build -t ai-crm-backend:latest .

cd ../frontend
docker build -t ai-crm-frontend:latest .
```

### Run with Docker Compose

```bash
# Set environment variables
export GROQ_API_KEY=your_groq_api_key

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

---

## ☁️ Cloud Deployment

### Option A: Railway.app (Backend)

**Pros:** Simple, free tier available, built-in database  
**Cost:** $5/month per service (free tier limits)

#### Steps:

1. **Push code to GitHub**

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Railway**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository
   - Configure environment variables:
     ```
     GROQ_API_KEY=your_key
     DEBUG=False
     ```
   - Deploy!

3. **Add MySQL Database**
   - In Railway dashboard
   - Click "Add MySQL"
   - Copy DATABASE_URL
   - Add to environment variables

### Option B: Render.com (Backend)

**Pros:** Generous free tier, automatic deploys  
**Cost:** Free tier or $7/month Pro

#### Steps:

1. **Connect GitHub repository**
   - https://render.com
   - New → Web Service
   - Connect GitHub account
   - Select repository

2. **Configure**
   - Environment: Python 3.11
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - Add environment variables

3. **Database**
   - New PostgreSQL database (or use external MySQL)
   - Update DATABASE_URL

4. **Deploy**
   - Render auto-deploys on GitHub push

### Option C: AWS (Full Stack)

**Pros:** Scalable, feature-rich  
**Cost:** Variable ($20-100+/month)

#### Architecture:

```
AWS EC2 (Backend)
    ↓
AWS RDS (MySQL)

CloudFront CDN
    ↓
S3 (Frontend)
    ↓
Route 53 (DNS)

Groq API (LLM)
```

#### Steps:

1. **EC2 Instance**

   ```bash
   # SSH into instance
   ssh -i key.pem ubuntu@public-ip

   # Install dependencies
   sudo apt update && sudo apt install -y python3.11 pip

   # Clone repo, setup, run backend
   ```

2. **RDS Database**
   - Create MySQL database
   - Get connection string
   - Add to EC2 environment variables

3. **S3 + CloudFront**
   - Build frontend: `npm run build`
   - Upload `dist/` to S3
   - Create CloudFront distribution
   - Point to S3

4. **Route 53**
   - Create DNS records
   - Point to CloudFront and EC2

### Option D: Heroku (Legacy but still works)

**Deprecated but still functional**

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create ai-crm-backend

# Add MySQL addon
heroku addons:create cleardb:ignite

# Deploy
git push heroku main

# Set environment
heroku config:set GROQ_API_KEY=your_key
```

---

## 🌐 Frontend Deployment

### Option 1: Vercel (Recommended)

**Pros:** Optimized for Next.js/React, free tier  
**Cost:** Free or $20/month Pro

#### Steps:

1. **Build frontend**

   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy**
   - https://vercel.com
   - Import Git repository
   - Configure build settings:
     - Framework: Vite
     - Build Command: `npm run build`
     - Output Directory: `dist`
   - Set environment:
     ```
     VITE_API_URL=https://your-backend-domain.com
     ```
   - Deploy!

### Option 2: Netlify

**Pros:** Simple, continuous deployment  
**Cost:** Free with generous limits

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod --dir=dist
```

### Option 3: GitHub Pages

**Cost:** Free  
**Limitation:** No backend, API must be CORS-enabled

```bash
# In package.json, add:
"homepage": "https://username.github.io/ai-crm-hcp"

# Deploy
npm run build
npm run deploy
```

### Option 4: S3 + CloudFront

```bash
# Build
npm run build

# Deploy to S3
aws s3 sync dist/ s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id E123 --paths "/*"
```

---

## 🔧 Production Configuration

### Backend (.env Production)

```env
# Database (use managed service)
DATABASE_URL=mysql+pymysql://user:pass@prod-db.com:3306/ai_crm_hcp

# LLM
GROQ_API_KEY=prod_groq_key_here

# Security
SECRET_KEY=very-long-random-secure-key-here
DEBUG=False

# CORS (production domains)
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Server
WORKERS=4
```

### Frontend (.env Production)

```env
# API endpoint
VITE_API_URL=https://api.yourdomain.com

# Analytics (optional)
VITE_ANALYTICS_ID=gtag_id_here
```

---

## 🔐 Security Checklists

### Backend Security

- [ ] Remove DEBUG=True in production
- [ ] Generate strong SECRET_KEY
- [ ] Use HTTPS only (SSL certificate)
- [ ] Restrict CORS to specific domains
- [ ] Enable database encryption
- [ ] Use environment variables for secrets
- [ ] Configure firewall rules
- [ ] Enable API rate limiting
- [ ] Set up monitoring/logging
- [ ] Use database backups

```python
# Production security settings
DEBUG = False
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]

# Enable HTTPS
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

### Frontend Security

- [ ] Enable HTTPS
- [ ] Set security headers
- [ ] Hide API keys (none should be in frontend)
- [ ] Implement CSP (Content Security Policy)
- [ ] Validate all user input
- [ ] Enable CORS properly

```html
<!-- Security Headers -->
<meta http-equiv="X-UA-Compatible" content="ie=edge" />
<meta name="referrer" content="strict-origin-when-cross-origin" />
<meta
  http-equiv="Content-Security-Policy"
  content="default-src 'self'; script-src 'self' 'unsafe-inline'"
/>
```

### Database Security

- [ ] Strong password (min 20 chars, uppercase, lowercase, numbers, symbols)
- [ ] Limited user privileges (don't use root)
- [ ] Encryption at rest
- [ ] Encryption in transit (SSL)
- [ ] Regular backups
- [ ] Automated patching
- [ ] Access logging

```bash
# Create limited user
CREATE USER 'crm_prod'@'%' IDENTIFIED BY 'very-long-secure-password';
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_crm_hcp.* TO 'crm_prod'@'%';
FLUSH PRIVILEGES;
```

---

## 📊 Monitoring & Logging

### Application Monitoring Tools

```python
# sentry.io (error tracking)
pip install sentry-sdk

import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
    traces_sample_rate=1.0
)
```

### Logging Setup

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ai-crm/app.log'),
        logging.StreamHandler()
    ]
)
```

### Uptime Monitoring

- **UptimeRobot**: Free uptime monitoring
- **Datadog**: Comprehensive monitoring
- **New Relic**: Application performance monitoring

---

## 🚀 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install backend dependencies
        run: |
          pip install -r backend/requirements.txt

      - name: Run backend tests
        run: pytest backend/

      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Build frontend
        run: |
          cd frontend
          npm install
          npm run build

      - name: Deploy to production
        run: |
          # Your deployment commands here
```

---

## 📈 Scaling Strategies

### Database Scaling

```sql
-- Add indexes for common queries
CREATE INDEX idx_doctor_name_sentiment
ON interactions(doctor_name, sentiment);

-- Archive old interactions
INSERT INTO interactions_archive
SELECT * FROM interactions
WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
DELETE FROM interactions
WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

### Backend Scaling

```bash
# Horizontal scaling with load balancer
# Deploy multiple instances behind load balancer
# Use auto-scaling groups (AWS)
```

### Frontend Caching

```javascript
// Service Worker for offline support
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js");
}
```

---

## 🔄 Continuous Deployment

### Auto-Deploy on Push

**Vercel/Netlify:**

- Connected to GitHub
- Auto-deploys on push to main
- Preview deployments on PRs

**Railway/Render:**

- Auto-deploys on connected GitHub repo
- Environment variables managed in dashboard

**AWS CodePipeline:**

```yaml
pipeline:
  source:
    github: your-repo
  build:
    docker-build: backend, frontend
  deploy:
    target: EC2, S3
```

---

## 🆘 Troubleshooting Production Issues

### Backend Down

```bash
# Check logs
docker logs container_name

# Restart service
docker restart container_name

# Check database connection
mysql -h db-host -u user -p -e "SELECT 1;"

# Check Groq API
curl https://api.groq.com/health
```

### Frontend Not Loading

```bash
# Check CloudFront cache
aws cloudfront create-invalidation --distribution-id E123 --paths "/*"

# Verify S3 bucket
aws s3 ls s3://bucket-name

# Check DNS
nslookup yourdomain.com
```

### High Memory Usage

```bash
# Monitor processes
top

# Increase container limits
# In docker-compose.yml:
services:
  backend:
    mem_limit: 2g
```

---

## 📝 Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed
- [ ] Secrets in .env (not in code)
- [ ] Database backups configured
- [ ] SSL certificates ready
- [ ] Domain DNS configured
- [ ] Monitoring setup

### During Deployment

- [ ] Enable verbose logging
- [ ] Monitor real-time logs
- [ ] Keep rollback plan ready
- [ ] Test critical flows

### Post-Deployment

- [ ] Verify services running
- [ ] Test all endpoints
- [ ] Check database integrity
- [ ] Monitor error rates
- [ ] Monitor performance
- [ ] Document deployment

---

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **AWS Docs**: https://docs.aws.amazon.com
- **Docker Docs**: https://docs.docker.com

---

**Deployment Guide v1.0**  
_for AI-CRM HCP Module_

Happy deploying! 🚀
