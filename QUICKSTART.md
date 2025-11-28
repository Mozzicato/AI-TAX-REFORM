# NTRIA QUICKSTART GUIDE

A step-by-step guide to get the NTRIA Graph RAG system up and running locally.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Initial Setup](#initial-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Hardware
- **Minimum:** 4GB RAM, 10GB disk space
- **Recommended:** 8GB+ RAM, 20GB+ disk space (for Neo4j and embeddings cache)

### Software
- **Node.js:** v18.0+ ([Install](https://nodejs.org/))
- **Python:** 3.9+ ([Install](https://www.python.org/downloads/))
- **Git:** ([Install](https://git-scm.com/))
- **Docker** (optional, for Neo4j): ([Install](https://www.docker.com/))

### API Keys Required
1. **OpenAI API Key** - For GPT-4 and embeddings
2. **Neo4j Cloud Account** - For knowledge graph (or local Docker instance)
3. **Pinecone Account** (optional) - For vector database (or use local Chroma)

---

## Initial Setup

### 1. Clone and Navigate to Repository

```bash
git clone <repository-url>
cd AI-TAX-REFORM
```

### 2. Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
# .env file

# ===== OPENAI =====
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# ===== NEO4J =====
NEO4J_URI=neo4j+s://your-neo4j-cloud-instance.com
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# ===== PINECONE (optional) =====
USE_PINECONE=false
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=ntria-tax-knowledge
PINECONE_ENVIRONMENT=us-west2-az1

# ===== BACKEND =====
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=true

# ===== FRONTEND =====
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Backend Setup

### 1. Create Python Virtual Environment

```bash
cd backend
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages including:
- FastAPI (web framework)
- Neo4j (graph database)
- Pinecone/Chroma (vector databases)
- LangChain (LLM orchestration)
- OpenAI (LLM API)
- And more...

### 3. Verify Installation

```bash
python -c "import fastapi, neo4j, openai; print('✅ All dependencies installed!')"
```

---

## Frontend Setup

### 1. Install Node Dependencies

```bash
cd frontend
npm install
```

This installs:
- Next.js 14
- React 18
- Tailwind CSS
- Axios (API client)
- TypeScript

### 2. Verify Installation

```bash
npm list next react tailwindcss
```

---

## Configuration

### Backend Configuration

#### Option 1: Local Neo4j with Docker

```bash
# Start Neo4j container
docker run \
  -p 7687:7687 \
  -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Update .env
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

#### Option 2: Neo4j Cloud

1. Create account at https://neo4j.com/cloud/
2. Create a new database instance
3. Get credentials from dashboard
4. Update `.env` with URI and credentials

### Vector Database Configuration

#### Option 1: Local Chroma (Default)

No additional setup required. Chroma is installed with requirements.txt and runs locally.

```bash
# .env
USE_PINECONE=false
```

#### Option 2: Pinecone Cloud

```bash
# Create Pinecone account and index at https://www.pinecone.io
# Update .env
USE_PINECONE=true
PINECONE_API_KEY=your-key
PINECONE_INDEX_NAME=ntria-tax-knowledge
PINECONE_ENVIRONMENT=us-west2-az1
```

### OpenAI Configuration

```bash
# Get API key from https://platform.openai.com/api-keys
# Update .env
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

---

## Running the Application

### 1. Start Backend Server

```bash
cd backend

# Activate virtual environment (if not already activated)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Start FastAPI server
python app/main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

The API will be available at:
- **API Base:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

### 2. Start Frontend Server (New Terminal)

```bash
cd frontend
npm run dev
```

Expected output:
```
- Local:        http://localhost:3000
- Environments: .env.local
```

Open http://localhost:3000 in your browser.

### 3. Test the Application

1. Navigate to http://localhost:3000
2. Ask a question: "What are the VAT registration requirements?"
3. You should see a response with sources and confidence score

---

## Testing

### Run Backend Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_chat_endpoints.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Run Frontend Tests

```bash
cd frontend

# Run Jest tests
npm test

# Run with coverage
npm test -- --coverage
```

### Manual API Testing

Use Swagger UI for interactive testing:

1. Navigate to http://localhost:8000/api/docs
2. Expand the "/api/v1/chat" endpoint
3. Click "Try it out"
4. Enter test message: `{"message": "What is VAT?"}`
5. Click "Execute"

---

## Processing Tax Documents

### 1. Prepare Documents

```bash
# Place PDF documents in data folder
mkdir -p data/raw
cp Nigeria-Tax-Act-2025.pdf data/raw/
```

### 2. Extract Text from PDFs

```bash
cd scripts
python extract_pdf.py ../data/raw/Nigeria-Tax-Act-2025.pdf
# Output: data/chunked/Nigeria-Tax-Act-2025.json
```

### 3. Extract Entities

```bash
python extract_entities.py ../data/chunked/Nigeria-Tax-Act-2025.json
# Output: data/extracted/entities.json, relationships.json
```

This will extract:
- Tax types, taxpayers, agencies
- Processes, thresholds, deadlines
- Relationships between entities

### 4. Populate Neo4j Graph

```bash
python populate_graph.py ../data/extracted/
# Populates Neo4j with 10 entity types and 12 relationship types
```

### 5. Generate Embeddings

```bash
python generate_embeddings.py ../data/chunked/
# Generates vector embeddings and populates vector DB (Pinecone or Chroma)
```

### 6. Verify Graph Population

Check Neo4j Browser:

```bash
# Navigate to http://localhost:7474 (local) or Neo4j Cloud console
# Run query:
MATCH (n) RETURN COUNT(n) as total_nodes
MATCH ()-[r]-() RETURN COUNT(r) as total_relationships
```

---

## Troubleshooting

### Backend Issues

#### "Connection refused" to Neo4j

```bash
# Check Neo4j is running
docker ps | grep neo4j

# If not running, start it
docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

#### "OpenAI API key not found"

```bash
# Check .env file exists and has OPENAI_API_KEY
cat .env | grep OPENAI_API_KEY

# If missing, add it:
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

#### "ModuleNotFoundError"

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or upgrade pip
pip install --upgrade pip
```

### Frontend Issues

#### Port 3000 already in use

```bash
# Run on different port
npm run dev -- -p 3001

# Or update NEXT_PUBLIC_API_URL if using different port
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

#### "Cannot GET /api/v1/chat"

Make sure:
1. Backend is running: `python backend/app/main.py`
2. Frontend .env has correct API URL: `NEXT_PUBLIC_API_URL=http://localhost:8000`
3. Check browser console for CORS errors

### API Connection Issues

#### CORS Errors

```bash
# Check CORS configuration in backend .env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Or test directly with curl
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

#### Slow Responses

1. Check OpenAI API status: https://status.openai.com/
2. Monitor Neo4j query performance
3. Check network connectivity
4. Try with shorter queries first

---

## Next Steps

1. **Process Tax Documents:** Follow the "Processing Tax Documents" section above
2. **Customize Knowledge Graph:** Edit schema in `graph/schema.cypher`
3. **Fine-tune Prompts:** Adjust system prompts in `backend/app/services/generator.py`
4. **Deploy:** See DEPLOYMENTGUIDE.md for production deployment

---

## Common Commands

```bash
# Start everything in development
# Terminal 1 - Backend
cd backend && source venv/bin/activate && python app/main.py

# Terminal 2 - Frontend
cd frontend && npm run dev

# Terminal 3 - Neo4j (if using Docker)
docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j:latest

# Test API endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is VAT?"}'

# View API documentation
open http://localhost:8000/api/docs
open http://localhost:3000
```

---

## Support

For issues, see:
- **DESIGNDOC.md** - Architecture details
- **README.md** - Feature overview
- **Backend issues** - Check `backend/app/main.py` and service modules
- **Frontend issues** - Check `frontend/src/hooks/useChat.ts`

---

**Happy coding! 🚀**
