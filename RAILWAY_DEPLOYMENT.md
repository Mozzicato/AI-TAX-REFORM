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

# DEPRECATED: Railway deployment guide

This document used to contain step-by-step instructions to deploy the backend to Railway.
The project has migrated to Render as the primary deployment target. Please see
`RENDER_DEPLOYMENT_INSTRUCTIONS.txt` at the repository root for the up-to-date,
exhaustive Render deployment guide, environment variable recommendations, health-checks,
debugging tips and frontend integration steps.

If you still need the old Railway guide for historical reasons, consult your Git history
or search for earlier commits that contain the original content.

-- Maintainers
   - Build the Docker image
