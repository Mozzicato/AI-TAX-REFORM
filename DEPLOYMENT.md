# NTRIA Deployment Guide

Complete guide for deploying the Graph RAG system to production.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
3. [Backend Deployment (Render)](#backend-deployment-render)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [Post-Deployment Testing](#post-deployment-testing)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Development Environment
- [ ] All tests passing locally (`pytest tests/`)
- [ ] Frontend builds successfully (`npm run build`)
- [ ] No console errors or warnings
- [ ] Environment variables documented
- [ ] Git repository clean and pushed

### API Credentials
- [ ] OpenAI API key tested and working
- [ ] Neo4j credentials verified
- [ ] Pinecone (or Chroma) configured
- [ ] API rate limits reviewed

### Data Pipeline
- [ ] Tax documents downloaded
- [ ] Entity extraction completed
- [ ] Neo4j graph populated
- [ ] Vector embeddings generated
- [ ] Sample queries verified

### Documentation
- [ ] README.md up to date
- [ ] QUICKSTART.md accurate
- [ ] API-DOCS.md complete
- [ ] DESIGNDOC.md reviewed

---

## Frontend Deployment (Vercel)

### 1. Create Vercel Account

Visit https://vercel.com and sign up with GitHub account.

### 2. Connect GitHub Repository

```bash
# In Vercel dashboard:
1. Click "New Project"
2. Select GitHub repository
3. Click "Import"
```

### 3. Configure Build Settings

| Setting | Value |
|---------|-------|
| Framework Preset | Next.js |
| Build Command | `npm run build` |
| Output Directory | `.next` |
| Install Command | `npm install` |

### 4. Set Environment Variables

In Vercel project settings, add:

```
NEXT_PUBLIC_API_URL=https://api.ntria.com
```

Or for staging:

```
NEXT_PUBLIC_API_URL=https://api-staging.ntria.com
```

### 5. Deploy

```bash
# Deploy on GitHub push (Vercel Auto-Deploy)
# Or manually:
vercel --prod
```

### 6. Verify Deployment

```bash
# Visit your Vercel URL
https://ntria-<id>.vercel.app

# Check build logs
vercel logs
```

---

## Backend Deployment (Render)

### 1. Create Render Account

Visit https://render.com and sign up.

### 2. Create Web Service

```
1. Click "New +"
2. Select "Web Service"
3. Connect GitHub repository
4. Select backend directory
```

### 3. Configure Service

| Setting | Value |
|---------|-------|
| Name | ntria-backend |
| Environment | Python 3.9 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### 4. Set Environment Variables

Add environment variables in Render dashboard:

```
OPENAI_API_KEY=sk-...
NEO4J_URI=neo4j+s://...
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...
PINECONE_API_KEY=...
ALLOWED_ORIGINS=https://ntria.vercel.app,https://ntria.com
BACKEND_PORT=8000
DEBUG=false
```

### 5. Deploy

Push to GitHub to trigger auto-deployment:

```bash
git push origin main
```

Or manually in Render dashboard:
- Click "Manual Deploy"
- Select branch
- Click "Deploy latest commit"

### 6. Verify Deployment

```bash
# Check deployment status
curl https://ntria-api.onrender.com/health

# Expected response:
{"status": "healthy", "service": "NTRIA API", "version": "1.0.0"}

# Check API docs
https://ntria-api.onrender.com/api/docs
```

---

## Alternative: Railway.app

### 1. Create Railway Account

Visit https://railway.app and sign up with GitHub.

### 2. Create New Project

```
1. Click "New Project"
2. Select "Deploy from GitHub"
3. Select repository
```

### 3. Configure Service

Add service configuration in `railway.json`:

```json
{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

### 4. Set Environment Variables

In Railway project settings, add environment variables.

### 5. Deploy

```bash
# Push to GitHub to auto-deploy
git push origin main
```

---

## Environment Configuration

### Production Environment File

Create `.env.production` with production values:

```bash
# OpenAI
OPENAI_API_KEY=sk-prod-key
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Neo4j
NEO4J_URI=neo4j+s://production-instance.com
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=production-password

# Pinecone
USE_PINECONE=true
PINECONE_API_KEY=prod-key
PINECONE_INDEX_NAME=ntria-prod
PINECONE_ENVIRONMENT=production

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=false

# Frontend
NEXT_PUBLIC_API_URL=https://api.ntria.com

# CORS
ALLOWED_ORIGINS=https://ntria.com,https://www.ntria.com

# Security
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
```

### Secrets Management

**Vercel:**
```bash
# Use Vercel built-in secrets
vercel env add OPENAI_API_KEY
vercel env add NEO4J_PASSWORD
```

**Render:**
```
Use Render dashboard Environment tab
- Sensitive values marked as "sensitive"
- Not exposed in logs
```

**Railway:**
```
Use Railway Variables tab
- Click "Add Variable"
- Enter key and value
- Select "Sensitive" for secrets
```

---

## Database Setup

### Production Neo4j

#### Option 1: Neo4j Cloud (Recommended)

```bash
# 1. Create account at https://neo4j.com/cloud/
# 2. Create production instance
# 3. Get credentials:
#    - URI: neo4j+s://xxx.databases.neo4j.io
#    - Username: neo4j
#    - Password: [auto-generated]
# 4. Add to environment:
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
```

#### Option 2: Self-Hosted Neo4j

```bash
# Deploy Neo4j on VPS
docker run -d \
  --name neo4j \
  -p 7687:7687 \
  -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/production-password \
  neo4j:latest

# Backup and restore:
# Use Neo4j backup tools for production data
```

### Production Vector Database

#### Option 1: Pinecone Cloud

```bash
# 1. Create production index at https://www.pinecone.io
# 2. Configuration:
#    - Dimension: 1536 (for text-embedding-3-small)
#    - Metric: cosine
#    - Environment: production
# 3. Add credentials:
PINECONE_API_KEY=production-key
PINECONE_INDEX_NAME=ntria-prod
```

#### Option 2: Self-Hosted Chroma

```bash
# Run Chroma server on separate VPS
docker run -d \
  -p 8000:8000 \
  -v chroma-data:/chroma/data \
  chromadb/chroma:latest

# Connect in backend:
CHROMA_HOST=chroma-server.example.com
CHROMA_PORT=8000
```

---

## Post-Deployment Testing

### 1. Health Checks

```bash
# Check frontend
curl https://ntria.vercel.app

# Check backend health
curl https://api.ntria.com/health

# Check API endpoints
curl https://api.ntria.com/api/v1/info
```

### 2. Functional Testing

```bash
# Send test question
curl -X POST https://api.ntria.com/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is VAT?"
  }'

# Check response
# Should receive answer, sources, and confidence score
```

### 3. Load Testing

```bash
# Using Apache Bench
ab -n 100 -c 10 https://api.ntria.com/health

# Using wrk
wrk -t4 -c100 -d30s https://api.ntria.com/health
```

### 4. Database Verification

```bash
# Neo4j query
curl -X POST https://api.ntria.com/api/v1/graph/search \
  -H "Content-Type: application/json" \
  -d '{
    "cypher": "MATCH (n) RETURN COUNT(n) as total"
  }'

# Should show entity count
```

---

## Monitoring & Logging

### Vercel Monitoring

```
1. Dashboard → Project → Analytics
2. Monitor:
   - Page loads
   - Edge Function duration
   - Build times
3. Set up alerts for anomalies
```

### Render Monitoring

```
1. Dashboard → Service → Logs
2. View:
   - Deployment logs
   - Runtime logs
   - Error logs
3. Set up Slack notifications
```

### Application Logging

Add logging to FastAPI:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    logger.info(f"Chat request: {request.message}")
    try:
        response = await process_chat(request)
        logger.info(f"Chat response: confidence={response.confidence}")
        return response
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise
```

### Error Tracking

Setup Sentry for error monitoring:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/123456",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1
)
```

---

## Security Hardening

### 1. Enable HTTPS

All production deployments automatically use HTTPS (Vercel, Render).

### 2. Set CORS Headers Properly

```python
# Only allow frontend domain
ALLOWED_ORIGINS = ["https://ntria.com", "https://www.ntria.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    max_age=86400
)
```

### 3. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/chat")
@limiter.limit("100/minute")
async def chat(request: Request, data: ChatRequest):
    # Implementation
    pass
```

### 4. Input Validation

```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=5000)
    session_id: Optional[str] = Field(None, max_length=50)
```

### 5. API Key Protection

```python
# Use environment variables, never commit keys
# Use secrets manager in hosting platform
# Rotate keys regularly
# Monitor usage patterns
```

---

## Backup & Disaster Recovery

### 1. Database Backups

```bash
# Neo4j backup
neo4j-admin backup --database=neo4j --backup-path=/backups

# Schedule daily backups
0 2 * * * /usr/bin/neo4j-admin backup --database=neo4j --backup-path=/backups

# Test restore
neo4j-admin restore --database=neo4j --from=/backups/neo4j-backup
```

### 2. Disaster Recovery Plan

- **RTO (Recovery Time Objective):** 1 hour
- **RPO (Recovery Point Objective):** 24 hours

```bash
# Backup strategy:
1. Hourly database snapshots
2. Daily code backups
3. Weekly full backups to S3
4. Monthly test restores

# Failover procedure:
1. Detect failure
2. Activate backup instance
3. Update DNS/routing
4. Notify users
5. Root cause analysis
```

---

## Performance Optimization

### 1. CDN Configuration (Vercel)

- Automatically configured
- Static assets cached
- API routes optimized

### 2. Database Query Optimization

```cypher
# Add indices for frequently queried properties
CREATE INDEX idx_tax_name FOR (t:Tax) ON (t.name);
CREATE INDEX idx_taxpayer_type FOR (tp:Taxpayer) ON (tp.type);
```

### 3. Response Caching

```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

@app.get("/api/v1/entities")
@cached(expire=3600)
async def get_entities(entity_type: Optional[str] = None):
    # Cached for 1 hour
    return entities
```

---

## Troubleshooting

### Issue: "Connection refused" to Neo4j

```bash
# Check Neo4j is running
curl https://your-neo4j-instance/

# Check credentials
NEO4J_URI=neo4j+s://correct-uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=correct-password

# View backend logs
vercel logs
```

### Issue: CORS errors on frontend

```bash
# Check ALLOWED_ORIGINS includes frontend URL
ALLOWED_ORIGINS=https://ntria.vercel.app

# Test with curl
curl -H "Origin: https://ntria.vercel.app" \
  -X POST https://api.ntria.com/api/v1/chat
```

### Issue: Slow API responses

```bash
# Check Neo4j query performance
# Add LIMIT clauses
MATCH (n:Tax) RETURN n LIMIT 100

# Monitor query times
neo4j-admin query-log

# Consider adding indices
CREATE INDEX idx_name FOR (n:Tax) ON (n.name);
```

### Issue: Out of memory errors

```bash
# Increase Render/Railway memory
# Edit service configuration
# Memory: 512MB → 1GB

# Monitor memory usage
ps aux | grep uvicorn
free -m
```

---

## Rollback Procedure

### If Deployment Fails

#### Vercel Rollback

```
1. Dashboard → Deployments
2. Find previous working deployment
3. Click "..."
4. Select "Promote to Production"
```

#### Render Rollback

```
1. Dashboard → Deploys
2. Find previous deployment
3. Click "Redeploy"
```

### Git Rollback

```bash
# Find good commit
git log --oneline | head -20

# Revert
git revert HEAD
git push origin main

# Trigger re-deployment
# Vercel/Render auto-deploy on push
```

---

## Maintenance & Updates

### Regular Maintenance

```bash
# Weekly
- Check error logs
- Monitor performance metrics
- Review user feedback

# Monthly
- Update dependencies
- Run security audit
- Backup verification
- Performance review

# Quarterly
- Major version updates
- Architecture review
- Capacity planning
- Disaster recovery test
```

### Security Updates

```bash
# Monitor for CVEs
npm audit
pip audit

# Apply patches
npm update
pip install --upgrade -r requirements.txt

# Test thoroughly before deploying
pytest tests/
npm run build
```

---

## Support & Escalation

### Emergency Contact

- **Critical Issue:** Immediate response
- **High Priority:** 4-hour response
- **Medium Priority:** 24-hour response
- **Low Priority:** 48-hour response

### Resources

- Vercel Support: https://vercel.com/help
- Render Support: https://render.com/docs
- Neo4j Support: https://support.neo4j.com
- OpenAI Support: https://help.openai.com

---

## Deployment Checklist

Before Going Live:

- [ ] All tests passing
- [ ] Environment variables set
- [ ] Database populated
- [ ] Health endpoints working
- [ ] API endpoints tested
- [ ] Frontend loads correctly
- [ ] Chat functionality works
- [ ] Error handling tested
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Rollback procedure documented
- [ ] Support team trained

---

**For detailed setup, see QUICKSTART.md**  
**For API reference, see API-DOCS.md**  
**For architecture details, see DESIGNDOC.md**
