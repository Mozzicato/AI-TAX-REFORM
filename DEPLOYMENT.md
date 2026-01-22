# 🚀 AI Tax Reform - Deployment Guide

Complete deployment guide for hosting the AI Tax Reform application on **Vercel** (frontend) and **Render** (backend).

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Backend Deployment (Render)](#backend-deployment-render)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Environment Variables](#environment-variables)
6. [Post-Deployment Testing](#post-deployment-testing)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐
│   Vercel        │         │   Render        │
│   (Frontend)    │────────>│   (Backend)     │
│   Next.js 14    │  HTTPS  │   Flask + RAG   │
└─────────────────┘         └─────────────────┘
                                    │
                                    ├── FAISS Vectorstore
                                    ├── Groq API
                                    └── Gemini API
```

- **Frontend**: Next.js app hosted on Vercel
- **Backend**: Flask API with RAG pipeline on Render
- **Storage**: FAISS vectorstore (local to backend)
- **AI Models**: Groq (primary), Gemini (fallback)

---

## ✅ Prerequisites

### Required Accounts
- [GitHub](https://github.com) account
- [Render](https://render.com) account (free tier available)
- [Vercel](https://vercel.com) account (free tier available)

### Required API Keys
- **Groq API Key**: Get from [console.groq.com](https://console.groq.com)
- **Gemini API Key**: Get from [ai.google.dev](https://ai.google.dev)

### Local Requirements (for testing)
- Git
- Python 3.11+
- Node.js 18+

---

## 🐍 Backend Deployment (Render)

### Step 1: Prepare Repository

1. **Push to GitHub** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/AI-TAX-REFORM.git
   git push -u origin main
   ```

2. **Verify required files exist**:
   - ✅ `requirements.txt` - Python dependencies
   - ✅ `runtime.txt` - Python version (3.11.0)
   - ✅ `gunicorn.conf.py` - Gunicorn configuration
   - ✅ `Procfile` or `render.yaml` - Render config
   - ✅ `vectorstore/` folder - Pre-generated embeddings

### Step 2: Create Render Web Service

1. **Go to [Render Dashboard](https://dashboard.render.com)**

2. **Click "New +" → "Web Service"**

3. **Connect GitHub repository**:
   - Authorize Render to access your GitHub
   - Select `AI-TAX-REFORM` repository

4. **Configure service**:
   ```
   Name:              ai-tax-reform-api
   Region:            Oregon (US West) or closest to you
   Branch:            main
   Root Directory:    (leave empty)
   Environment:       Python 3
   Build Command:     pip install -r requirements.txt
   Start Command:     gunicorn app:app --config gunicorn.conf.py
   Instance Type:     Free (or Starter for better performance)
   ```

### Step 3: Add Environment Variables

In Render dashboard, add these environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.11.0` | Match runtime.txt |
| `FLASK_ENV` | `production` | Production mode |
| `PORT` | `7860` | Default Flask port |
| `GROQ_API_KEY` | `gsk_...` | Your Groq API key |
| `GEMINI_API_KEY` | `AI...` | Your Gemini API key |
| `CORS_ORIGINS` | `https://your-frontend.vercel.app` | Update after frontend deployment |

### Step 4: Deploy Backend

1. **Click "Create Web Service"**
2. **Wait for build to complete** (5-10 minutes first time)
3. **Copy your backend URL**: `https://ai-tax-reform-api.onrender.com`

### Step 5: Test Backend

```bash
# Health check
curl https://ai-tax-reform-api.onrender.com/health

# Test QA endpoint
curl -X POST https://ai-tax-reform-api.onrender.com/api/qa \
  -H "Content-Type: application/json" \
  -d '{"query": "What is PAYE tax in Nigeria?"}'
```

---

## ⚡ Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Verify required files**:
   - ✅ `package.json` - Dependencies and build scripts
   - ✅ `next.config.js` - Next.js configuration
   - ✅ `vercel.json` - Vercel configuration
   - ✅ `.env.example` - Environment template

3. **Test build locally**:
   ```bash
   npm install
   npm run build
   npm start
   ```

### Step 2: Deploy to Vercel

#### Option A: Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd frontend
   vercel
   ```

4. **Follow prompts**:
   ```
   Set up and deploy? Yes
   Which scope? Your account
   Link to existing project? No
   Project name? ai-tax-reform
   Directory? ./
   Override settings? No
   ```

5. **Set environment variable**:
   ```bash
   vercel env add NEXT_PUBLIC_API_URL production
   # Enter your Render backend URL: https://ai-tax-reform-api.onrender.com
   ```

6. **Deploy to production**:
   ```bash
   vercel --prod
   ```

#### Option B: Vercel Dashboard

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**

2. **Click "Add New" → "Project"**

3. **Import Git Repository**:
   - Select your GitHub repository
   - Framework Preset: **Next.js**
   - Root Directory: **frontend**
   - Build Command: `npm run build`
   - Output Directory: `.next`

4. **Add Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL = https://ai-tax-reform-api.onrender.com
   ```

5. **Click "Deploy"**

6. **Copy your frontend URL**: `https://ai-tax-reform.vercel.app`

### Step 3: Update Backend CORS

1. **Go back to Render dashboard**
2. **Update `CORS_ORIGINS` environment variable**:
   ```
   https://ai-tax-reform.vercel.app,http://localhost:3000
   ```
3. **Redeploy backend** (or it will auto-redeploy)

---

## 🔐 Environment Variables

### Backend (.env on Render)

```bash
# Required
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxx
FLASK_ENV=production
PORT=7860

# CORS - Add your Vercel frontend URL
CORS_ORIGINS=https://ai-tax-reform.vercel.app,http://localhost:3000

# Optional (defaults shown)
MODEL_NAME=llama3-70b-8192
TEMPERATURE=0.1
MAX_TOKENS=1024
TOP_K=5
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Frontend (.env.local for Vercel)

```bash
# Required - Your Render backend URL
NEXT_PUBLIC_API_URL=https://ai-tax-reform-api.onrender.com
```

---

## 🧪 Post-Deployment Testing

### 1. Test Backend Health

```bash
curl https://ai-tax-reform-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "qa_service": "initialized",
  "calculator": "ready",
  "vectorstore_docs": 150
}
```

### 2. Test QA Endpoint

```bash
curl -X POST https://ai-tax-reform-api.onrender.com/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the tax rate for income above 3.2 million naira?",
    "use_verification": false
  }'
```

### 3. Test Calculator Endpoint

```bash
curl -X POST https://ai-tax-reform-api.onrender.com/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "annual_income": 5000000,
    "allowable_deductions": 500000
  }'
```

### 4. Test Frontend

1. Visit your Vercel URL: `https://ai-tax-reform.vercel.app`
2. Try the chat interface with a tax question
3. Use the tax calculator with sample income
4. Verify source citations appear correctly

---

## 🛠️ Troubleshooting

### Backend Issues

#### Build Fails on Render

**Problem**: Python dependencies fail to install

**Solutions**:
```bash
# Check requirements.txt has correct versions
# Verify runtime.txt specifies Python 3.11.0
# Check Render build logs for specific error
```

#### CORS Errors

**Problem**: Frontend can't connect to backend

**Solutions**:
1. Verify `CORS_ORIGINS` includes your Vercel URL
2. Check no trailing slash in URLs
3. Ensure both http and https variants if needed
4. Restart Render service after changing environment variables

#### Vectorstore Not Found

**Problem**: `FileNotFoundError: vectorstore/faiss_index.bin`

**Solutions**:
1. Ensure `vectorstore/` folder is committed to git
2. Run `python scripts/ingest_pdf.py` locally
3. Commit and push the generated vectorstore files
4. Redeploy on Render

#### API Key Errors

**Problem**: `401 Unauthorized` or `Invalid API key`

**Solutions**:
1. Verify API keys are correct in Render environment variables
2. Check for extra spaces or newlines in keys
3. Regenerate keys from Groq/Gemini consoles
4. Test keys locally first

#### Cold Start Delays

**Problem**: First request takes 30+ seconds

**Solutions**:
- This is normal on Render free tier (spins down after inactivity)
- Upgrade to Starter plan for always-on service
- Implement frontend loading states
- Use Render cron jobs to keep service warm

### Frontend Issues

#### Build Fails on Vercel

**Problem**: Next.js build errors

**Solutions**:
```bash
# Test build locally first
cd frontend
npm run build

# Check Node.js version matches (18+)
node --version

# Clear cache and reinstall
rm -rf .next node_modules package-lock.json
npm install
npm run build
```

#### API Requests Fail

**Problem**: Network errors or timeouts

**Solutions**:
1. Verify `NEXT_PUBLIC_API_URL` is correct
2. Check backend is running (test health endpoint)
3. Inspect browser console for CORS errors
4. Ensure no trailing slash in API URL

#### Environment Variables Not Working

**Problem**: API URL shows as `undefined`

**Solutions**:
1. Environment variables MUST start with `NEXT_PUBLIC_` for client-side access
2. Redeploy after adding/changing environment variables
3. Check Vercel dashboard → Settings → Environment Variables
4. For CLI: `vercel env pull` to sync locally

#### Styling Issues

**Problem**: Tailwind classes not applying

**Solutions**:
1. Verify `tailwind.config.ts` has correct content paths
2. Check `postcss.config.js` exists
3. Ensure CSS validation is disabled (see `.vscode/settings.json`)
4. Clear `.next` folder and rebuild

### General Issues

#### Rate Limiting

**Problem**: `429 Too Many Requests`

**Solutions**:
- Groq free tier: 30 requests/minute
- Implement request debouncing on frontend
- Add caching layer in backend
- Upgrade API plan if needed

#### Slow Response Times

**Problem**: Queries take 10+ seconds

**Solutions**:
1. Reduce `top_k` parameter (default: 5)
2. Disable answer verification for faster responses
3. Use Groq's faster models (llama3-8b instead of 70b)
4. Optimize chunking parameters in `ingest_pdf.py`

#### Memory Issues

**Problem**: Service crashes with OOM error

**Solutions**:
- Render free tier has 512MB RAM limit
- Reduce embedding model size
- Implement pagination for large result sets
- Upgrade to Render Starter plan (2GB RAM)

---

## 📊 Monitoring & Maintenance

### Render Monitoring

1. **View Logs**:
   - Dashboard → Your Service → Logs
   - Real-time log streaming
   - Filter by error/warning levels

2. **Metrics**:
   - CPU and memory usage
   - Request count and latency
   - Error rates

3. **Alerts**:
   - Set up email notifications for service failures
   - Monitor deployment status

### Vercel Monitoring

1. **Analytics**:
   - Dashboard → Analytics
   - Page views and performance
   - Real user metrics (Core Web Vitals)

2. **Logs**:
   - Dashboard → Deployments → Functions
   - Runtime logs for API routes
   - Error tracking

3. **Performance**:
   - Lighthouse scores
   - Build times
   - Bundle size analysis

### Cost Management

#### Render Free Tier Limits
- 750 hours/month (always-on for 1 service)
- 512MB RAM
- Spins down after 15 minutes of inactivity
- 100GB bandwidth/month

#### Vercel Free Tier Limits
- 100GB bandwidth/month
- 100 deployments/day
- Unlimited personal projects
- Serverless function execution: 100 hours/month

### Updating Your App

#### Backend Updates
```bash
# Make changes locally
git add .
git commit -m "Update backend logic"
git push origin main

# Render auto-deploys from main branch
# Monitor deployment in Render dashboard
```

#### Frontend Updates
```bash
# Make changes locally
cd frontend
npm run build  # Test locally first

# Deploy
git add .
git commit -m "Update frontend UI"
git push origin main

# Vercel auto-deploys from main branch
```

---

## 🎯 Production Checklist

Before going live, ensure:

### Backend
- [ ] All API keys are set in Render environment variables
- [ ] `CORS_ORIGINS` includes production frontend URL
- [ ] `FLASK_ENV=production`
- [ ] Vectorstore is committed to repository
- [ ] Health check endpoint returns 200
- [ ] All endpoints tested with curl/Postman
- [ ] Logs show no errors
- [ ] Gunicorn workers configured properly

### Frontend
- [ ] `NEXT_PUBLIC_API_URL` points to production backend
- [ ] Build completes successfully
- [ ] All pages load correctly
- [ ] Chat interface connects to backend
- [ ] Calculator returns correct results
- [ ] Mobile responsiveness verified
- [ ] SEO meta tags configured
- [ ] Error boundaries implemented

### Security
- [ ] API keys never exposed in frontend code
- [ ] CORS properly configured (not using `*`)
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] HTTPS enforced everywhere
- [ ] Secrets not committed to git

### Documentation
- [ ] README.md updated with live URLs
- [ ] API endpoints documented
- [ ] Environment variables documented
- [ ] Troubleshooting guide available

---

## 🔗 Useful Links

### Documentation
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [Next.js Docs](https://nextjs.org/docs)
- [Flask Docs](https://flask.palletsprojects.com)
- [FAISS Wiki](https://github.com/facebookresearch/faiss/wiki)

### API Providers
- [Groq Console](https://console.groq.com)
- [Google AI Studio](https://ai.google.dev)

### Monitoring Tools
- [Render Status](https://status.render.com)
- [Vercel Status](https://vercel-status.com)

---

## 📞 Support

If you encounter issues not covered in this guide:

1. Check Render/Vercel status pages
2. Review application logs
3. Test endpoints with curl
4. Verify environment variables
5. Open an issue on GitHub

---

**Happy Deploying! 🚀**

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy: Backend ready"
   git push origin main
   ```

2. **Create Render Web Service**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render will auto-detect `render.yaml`

3. **Set Environment Variables**:
   - `GROQ_API_KEY` - Your Groq API key
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - `CORS_ORIGINS` - Your Vercel frontend URL
   - `FLASK_ENV` - `production`

4. **Deploy**: Render will build and deploy automatically

### Deploy Frontend to Vercel

1. **Install Vercel CLI** (optional):
   ```bash
   npm i -g vercel
   ```

2. **Deploy via Dashboard**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New..." → "Project"
   - Import your GitHub repo
   - Set Root Directory to `frontend`
   - Add environment variable:
     - `NEXT_PUBLIC_API_URL` = Your Render backend URL

3. **Deploy via CLI**:
   ```bash
   cd frontend
   vercel --prod
   ```

## 🔧 Configuration

### Backend (.env)

```env
# Flask
FLASK_ENV=production
PORT=7860

# CORS (comma-separated)
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000

# LLM APIs
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIza...
HF_TOKEN=hf_...  # Optional
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:7860  # Development
# or
NEXT_PUBLIC_API_URL=https://your-api.onrender.com  # Production
```

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.1 + Flask-CORS
- **Vector DB**: FAISS (CPU)
- **Embeddings**: sentence-transformers (all-mpnet-base-v2)
- **LLMs**: Groq (llama-3.3-70b-versatile), Google Gemini (text-bison-001)
- **PDF Processing**: PyPDF2
- **Server**: Gunicorn (production)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI**: Lucide React icons
- **Markdown**: react-markdown + remark-gfm

### Infrastructure
- **Backend Hosting**: Render (Free tier available)
- **Frontend Hosting**: Vercel (Free tier available)
- **Version Control**: Git/GitHub

## 📊 RAG Pipeline

1. **Document Ingestion**:
   - Load PDF → Extract text → Chunk (500 chars, 100 overlap)
   - Generate embeddings (768-dim vectors)
   - Build FAISS index (IndexFlatIP for cosine similarity)

2. **Query Processing**:
   - Embed user query
   - Search FAISS index (top-k semantic matches)
   - Return relevant chunks with scores

3. **Answer Generation**:
   - Construct prompt with context chunks
   - Call Groq API (primary) or Gemini (fallback)
   - Return answer with sources and model info

4. **Verification** (optional):
   - Ask LLM to verify answer against sources
   - Return accuracy assessment

## 🔒 Security

- API keys stored in environment variables
- CORS configured for specific origins
- `.env` and sensitive files in `.gitignore`
- No credentials in version control
- Rate limiting recommended for production

## 🐛 Troubleshooting

### Backend Issues

**Vectorstore not found**:
```bash
python scripts/ingest_pdf.py
```

**Import errors (torch, transformers)**:
- Ensure compatible versions: PyTorch 2.0.1, sentence-transformers 2.2.2
- Windows: Install Visual C++ Redistributable

**API key errors**:
- Verify `.env` file exists and contains valid keys
- Check `python-dotenv` is installed

### Frontend Issues

**API connection failed**:
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify backend is running
- Check CORS configuration on backend

**Build errors**:
```bash
rm -rf .next node_modules
npm install
npm run build
```

## 📝 Development

### Add New Tax Document

1. Place PDF in `data/raw/`
2. Update `scripts/ingest_pdf.py` if needed
3. Run ingestion: `python scripts/ingest_pdf.py`
4. Restart backend

### Modify Tax Calculation Logic

Edit [src/tax_calculator.py](src/tax_calculator.py) and update the tax brackets or calculation logic.

### Add New LLM Provider

1. Add provider function in `scripts/qa_service.py`
2. Update `generate_answer()` fallback chain
3. Add API key to `.env`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Nigeria Tax Act 2025 (source document)
- Groq for fast LLM inference
- Google Gemini for fallback generation
- HuggingFace for transformer models
- FAISS for efficient vector search

## 📧 Contact

For questions or issues, please open a GitHub issue or contact the maintainers.

---

**Built with ❤️ for Nigerian taxpayers**
