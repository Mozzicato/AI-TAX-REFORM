# AI Tax Reform - RAG-Powered Tax Assistant 🇳🇬

An intelligent tax information and calculation system for Nigerian tax law, powered by Retrieval-Augmented Generation (RAG) and large language models.

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

## ✨ Features

### 💬 Intelligent Chat Interface
- Natural language questions about Nigerian tax law
- AI-powered answers using Groq (Llama 3.3 70B) and Google Gemini
- Real-time source citations with relevance scores
- Answer verification for enhanced accuracy
- Copy responses, view sources, retry on errors
- Suggested questions to get started

### 🧮 Comprehensive Tax Calculator
- Calculate personal income tax with detailed breakdowns
- Based on the **Nigeria Tax Act 2025**
- Progressive tax brackets: 7%, 11%, 15%, 19%, 21%, 24%
- **Consolidated Relief Allowance (CRA)** auto-calculation
- Pension contribution relief support
- Minimum tax (1% above ₦30M) handling
- Monthly and annual tax views
- Net income calculation

### 🔍 Advanced RAG Pipeline
- FAISS vector search for semantic retrieval
- Local sentence-transformers embeddings (768-dim)
- 1143+ chunks from Nigeria Tax Act 2025
- Sub-second query response times

### 🛡️ Production-Ready Features
- Rate limiting to prevent abuse
- Input validation and sanitization
- CORS security with configurable origins
- Structured error handling
- Request logging and monitoring
- API documentation endpoint

## 📊 Tax Brackets (Nigeria 2025)

| Income Range | Rate |
|-------------|------|
| First ₦300,000 | 7% |
| Next ₦300,000 | 11% |
| Next ₦500,000 | 15% |
| Next ₦500,000 | 19% |
| Next ₦1,600,000 | 21% |
| Above ₦3,200,000 | 24% |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- 2GB+ RAM

### 1. Clone and Setup Backend

```bash
git clone https://github.com/YOUR_USERNAME/AI-TAX-REFORM.git
cd AI-TAX-REFORM

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys (see .env.example for details)
```

### 2. Ingest Documents (First Time Only)

```bash
# Place your PDF in data/raw/Nigeria-Tax-Act-2025.pdf
python scripts/ingest_pdf.py --pdf data/raw/Nigeria-Tax-Act-2025.pdf
```

This creates the vectorstore (~1143 chunks, takes 2-3 minutes).

### 3. Run Backend

```bash
python app.py
```

Backend API runs at http://localhost:7860

### 4. Setup Frontend

```bash
cd frontend
npm install

# Run development server
npm run dev
```

Frontend runs at http://localhost:3000

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API documentation |
| `/health` | GET | Health check |
| `/calculate` | POST | Calculate personal income tax |
| `/retrieve` | POST | Retrieve relevant tax documents |
| `/qa` | POST | Ask questions (RAG) |
| `/aqa` | POST | Ask with verification |

### Example: Calculate Tax

```bash
curl -X POST http://localhost:7860/calculate \
  -H "Content-Type: application/json" \
  -d '{"income": 5000000, "allowances": 500000, "reliefs": 200000}'
```

### Example: Ask a Question

```bash
curl -X POST http://localhost:7860/qa \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the personal income tax rate in Nigeria?"}'
```

## 🌐 Deployment

### Deploy Backend to Render

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push origin main
   ```

2. **Create Web Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your repo
   - Render detects `render.yaml` automatically

3. **Set Environment Variables**:
   ```
   GROQ_API_KEY = gsk_...
   GEMINI_API_KEY = AIza...
   FLASK_ENV = production
   CORS_ORIGINS = https://your-frontend.vercel.app
   ```

4. **Deploy**: Render builds and deploys automatically (~5 min)

### Deploy Frontend to Vercel

1. **Via Dashboard**:
   - Go to [Vercel](https://vercel.com/new)
   - Import GitHub repo
   - Set Root Directory: `frontend`
   - Add environment variable:
     - `NEXT_PUBLIC_API_URL` = `https://your-api.onrender.com`
   - Deploy

2. **Via CLI**:
   ```bash
   cd frontend
   npm i -g vercel
   vercel --prod
   ```

**See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.**

## 📁 Project Structure

```
AI-TAX-REFORM/
├── app.py                    # Flask API (main)
├── requirements.txt          # Python dependencies
├── gunicorn.conf.py         # Production server config
├── Procfile                 # Render deployment
├── render.yaml              # Render blueprint
│
├── data/raw/                # Tax documents (PDFs)
│   └── Nigeria-Tax-Act-2025.pdf
│
├── scripts/
│   ├── ingest_pdf.py        # PDF → embeddings → vectorstore
│   ├── query_qa.py          # Vector search
│   └── qa_service.py        # Groq/Gemini integration
│
├── src/
│   └── tax_calculator.py    # Tax calculation logic
│
├── vectorstore/             # FAISS index (generated)
│   ├── faiss_index.bin
│   └── metadata.pkl
│
└── frontend/                # Next.js app
    ├── src/
    │   ├── app/            # Pages
    │   ├── components/     # React components
    │   └── lib/            # Utils
    ├── package.json
    └── vercel.json         # Vercel config
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/calculate` | POST | Tax calculation |
| `/retrieve` | POST | Document retrieval |
| `/qa` | POST | Question answering |
| `/aqa` | POST | Verified Q&A |

### Example: Question Answering

```bash
curl -X POST http://localhost:7860/qa \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the personal income tax threshold?",
    "top_k": 5
  }'
```

Response:
```json
{
  "answer": "The personal income tax threshold is ₦300,000...",
  "model": "groq",
  "sources": [
    {
      "text": "For the first ₦300,000...",
      "page": 12,
      "score": 0.42
    }
  ]
}
```

## 🛠️ Tech Stack

**Backend**:
- Flask 3.1 + Flask-CORS
- FAISS (vector search)
- sentence-transformers (all-mpnet-base-v2)
- PyTorch 2.0.1
- Groq API (llama-3.3-70b-versatile)
- Google Gemini API (text-bison-001)
- Gunicorn (production server)

**Frontend**:
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Markdown
- Lucide Icons

**Infrastructure**:
- Backend: Render (Python)
- Frontend: Vercel (Next.js)
- Version Control: Git/GitHub

## 📊 RAG Architecture

```
User Query
    ↓
Embed Query (sentence-transformers)
    ↓
FAISS Search (top-k=5, cosine similarity)
    ↓
Retrieve Context Chunks
    ↓
Build Prompt (query + contexts)
    ↓
LLM Generation (Groq → Gemini fallback)
    ↓
Answer + Sources
    ↓
[Optional] Verification
```

## ⚙️ Configuration

### Backend (.env)
```env
FLASK_ENV=production
PORT=7860
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIza...
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:7860  # Dev
# NEXT_PUBLIC_API_URL=https://api.onrender.com  # Prod
```

## 🔧 Development

### Add New Documents
```bash
# Add PDF to data/raw/
python scripts/ingest_pdf.py
# Restart backend
```

### Modify Tax Logic
Edit [src/tax_calculator.py](src/tax_calculator.py) and restart server.

### Add LLM Provider
1. Add function in `scripts/qa_service.py`
2. Update fallback chain in `generate_answer()`
3. Add API key to `.env`

## 🐛 Troubleshooting

**Vectorstore not found**:
```bash
python scripts/ingest_pdf.py
```

**Import errors (PyTorch/transformers)**:
- Windows: Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Verify versions: PyTorch 2.0.1, sentence-transformers 2.2.2

**Frontend can't connect**:
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify backend is running: `curl http://localhost:7860/health`
- Check CORS_ORIGINS in backend `.env`

## 📈 Performance

- **Vectorstore Load**: ~1s (cached after first load)
- **Query Embedding**: ~100ms
- **FAISS Search**: ~10ms for 1143 vectors
- **LLM Generation**: 1-3s (Groq), 2-5s (Gemini)
- **Total Response**: 1.5-4s end-to-end

## 🔒 Security

- API keys in environment variables only
- `.env` and secrets gitignored
- CORS configured for specific origins
- No credentials in version control
- Health check for monitoring

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push: `git push origin feature/name`
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- Nigeria Federal Inland Revenue Service (FIRS)
- Groq for fast LLM inference
- Google Gemini for reliable generation
- HuggingFace for transformer models
- FAISS for vector search

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/AI-TAX-REFORM/issues)
- **Docs**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Frontend**: [frontend/README.md](frontend/README.md)

---

**⚠️ Disclaimer**: This is an informational tool. Consult a licensed tax professional for official tax advice.

**Built with ❤️ for Nigerian taxpayers**


