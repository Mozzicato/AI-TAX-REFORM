---
title: AI TAX REFORM API
emoji: 📊
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# AI TAX REFORM - Nigeria Tax Reform Intelligence Assistant

**Graph RAG Backend API** - Powered by Gemini, Pinecone, and Knowledge Graphs

## Overview
This is the backend API for the AI-TAX-REFORM system. It provides:
- 📚 Graph-enhanced RAG for tax queries
- 🧠 Gemini LLM integration
- 🔍 Pinecone vector search
- 🗣️ Voice transcription support
- 📊 Tax document analysis

## API Endpoints

### Health Check
```bash
GET /health
```

### Chat Interface
```bash
POST /api/v1/chat/answer
Content-Type: application/json

{
  "query": "What is the new VAT rate?",
  "use_graph": true,
  "use_vector": true
}
```

### Response
```json
{
  "answer": "The new VAT rate is 7.5%...",
  "sources": [
    {
      "title": "Finance Act 2023",
      "section": "Section 45"
    }
  ]
}
```

## Documentation
- **Swagger UI:** `/api/docs`
- **ReDoc:** `/api/redoc`

## Environment Variables Required
- `GEMINI_API_KEY` - Google Gemini API key
- `PINECONE_API_KEY` - Pinecone vector database key
- `PINECONE_INDEX_NAME` - Pinecone index name (default: `ntria-tax`)
- `ALLOWED_ORIGINS` - CORS allowed origins (comma-separated)

## Features
✅ Graph-based retrieval  
✅ Vector similarity search  
✅ Multi-source context fusion  
✅ Conversation memory (via query rewriting)  
✅ Audio transcription (Gemini)  
✅ Citation tracking  

## Local Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

## Repository
https://github.com/Mozzicato/AI-TAX-REFORM
