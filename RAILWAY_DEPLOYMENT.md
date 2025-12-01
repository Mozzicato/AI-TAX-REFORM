# 🚀 Deploy NTRIA Backend to Railway

This guide walks you through deploying your FastAPI backend to Railway with Docker.

## Prerequisites

- Railway account (create at https://railway.app)
- Git repository pushed to GitHub
- Docker configured locally (optional, for testing)

---

## **Step 1: Create a Railway Account**

1. Go to https://railway.app/dashboard
2. Sign up with GitHub (recommended)
3. Authorize Railway to access your GitHub repositories

---

## **Step 2: Create a New Railway Project**

1. Click **"New Project"** on the dashboard
2. Select **"Deploy from GitHub repo"**
3. Select your repo: `Mozzicato/AI-TAX-REFORM`
4. Railway will auto-detect the Dockerfile

---

## **Step 3: Configure Environment Variables**

In Railway project settings, add these environment variables:

```env
# Database
NEO4J_URI=bolt://your-neo4j-instance:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# APIs
OPENAI_API_KEY=sk-your-key
PINECONE_API_KEY=your-key
PINECONE_INDEX_NAME=ntria

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app

# App
ENVIRONMENT=production
DEBUG=False
```

---

## **Step 4: Deploy**

1. Push your code to GitHub:
```bash
cd /workspaces/AI-TAX-REFORM
git add .
git commit -m "Dockerize backend for Railway deployment"
git push origin main
```

2. Railway will automatically:
   - Detect the Dockerfile
   - Build the Docker image
   - Deploy to Railway's infrastructure
   - Assign a public URL

3. Monitor deployment in **Railway Dashboard** → **Deployments** tab

---

## **Step 5: Get Your Backend URL**

After deployment completes:

1. Go to Railway Dashboard
2. Click on your project
3. Select the service (should be auto-named)
4. Copy the **Public URL** (e.g., `https://your-service.railway.app`)

---

## **Step 6: Update Frontend with Backend URL**

Update your Next.js frontend environment variables:

1. Deploy frontend to Vercel (see VERCEL_DEPLOYMENT.md)
2. Set `NEXT_PUBLIC_API_URL` to your Railway backend URL:
   ```
   NEXT_PUBLIC_API_URL=https://your-service.railway.app
   ```

---

## **Manual Testing (Local Docker)**

Test locally before deploying:

```bash
# Build Docker image
docker build -f backend/Dockerfile -t ntria-backend .

# Run container
docker run -p 8000:8000 \
  -e NEO4J_URI=bolt://localhost:7687 \
  -e OPENAI_API_KEY=your-key \
  ntria-backend

# Test health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "NTRIA API",
  "version": "1.0.0"
}
```

---

## **Troubleshooting**

### Build Fails
- Check `requirements.txt` for incompatible versions
- Review Railway logs in **Deployments** tab
- Verify Dockerfile paths are correct

### App Crashes After Deploy
- Check Railway logs for error messages
- Verify environment variables are set correctly
- Ensure Neo4j and API keys are valid

### Database Connection Error
```
Error: Could not connect to Neo4j
```
- Verify `NEO4J_URI` is correct
- Check Neo4j is running and accessible
- Verify credentials in environment variables

### Port Issues
```
Address already in use
```
- Railway automatically assigns `$PORT` environment variable
- Dockerfile already listens on `$PORT`
- No manual port configuration needed

---

## **Monitoring & Logs**

View your backend logs:

1. Railway Dashboard → Your Project
2. Click **"Logs"** tab
3. Real-time logs appear as requests come in

Example useful logs:
```
2025-12-01 10:30:15 - INFO - Application startup complete
2025-12-01 10:30:20 - INFO - GET /health - 200
2025-12-01 10:30:25 - INFO - POST /api/chat - 200
```

---

## **Scaling & Performance**

Railway settings for production:

1. **Memory**: Start with 512MB, scale up if needed
2. **Replicas**: For high traffic, enable auto-scaling
3. **Region**: Choose closest to your users

---

## **Environment Setup**

### Production Environment Variables

```env
# Required
NEO4J_URI=bolt://your-neo4j:7687
OPENAI_API_KEY=sk-xxx
PINECONE_API_KEY=xxx

# Recommended
ALLOWED_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Optional
PINECONE_INDEX_NAME=ntria
BATCH_SIZE=32
MAX_RETRIES=3
```

### Database Setup

If using Railway for Neo4j:

1. In Railway: **"New Plugin"** → **"Neo4j"**
2. Railway auto-generates connection string
3. Copy credentials to environment variables

---

## **Your Deployment URLs**

| Component | URL |
|-----------|-----|
| **Backend API** | `https://your-service.railway.app` |
| **API Docs** | `https://your-service.railway.app/api/docs` |
| **Health Check** | `https://your-service.railway.app/health` |

---

## **Next Steps**

1. ✅ Deploy backend to Railway
2. 📊 Deploy frontend to Vercel (see separate guide)
3. 🔗 Connect frontend to backend API URL
4. 🧪 Test end-to-end integration
5. 🚀 Monitor logs and performance

---

## **Support & Resources**

- [Railway Docs](https://docs.railway.app)
- [Docker Docs](https://docs.docker.com)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment)
- [GitHub Issues](https://github.com/Mozzicato/AI-TAX-REFORM/issues)

---

**Happy deploying! 🚀🇳🇬**
