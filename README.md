# 🇳🇬 NTRIA - Nigeria Tax Reform Intelligence Assistant

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Project Status](https://img.shields.io/badge/status-MVP%20Development-yellow.svg)]()
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)]()
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)]()

---

## **🎯 Project Overview**

**NTRIA** is an intelligent AI assistant that helps Nigerian students, NYSC participants, entrepreneurs, and citizens understand and navigate the **2025 Tax Reform Act**. 

Built with **Graph-enhanced Retrieval-Augmented Generation (Graph RAG)**, NTRIA provides accurate tax guidance, multi-step compliance recommendations, deadline alerts, and personalized advice.

**Status:** MVP Development for Tax Reform Challenge 2025

---

## **🚀 Quick Start**

```bash
# Clone & Setup
git clone https://github.com/Mozzicato/AI-TAX-REFORM.git
cd AI-TAX-REFORM
cp .env.example .env  # Add your API keys

# Frontend
cd frontend && npm install && npm run dev

# Backend (new terminal)
cd backend && python -m venv venv
source venv/bin/activate && pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit **http://localhost:3000**

---

## **📚 Documentation**

- [🔧 Full Architecture](DESIGNDOC.md) - Graph RAG system design
- [📋 Development Tasks](TODO.txt) - Step-by-step roadmap

---

## **📦 Tech Stack**

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js + React + Tailwind CSS |
| Backend | FastAPI + Python |
| Graph DB | Neo4j |
| Vector DB | Pinecone / Chroma |
| LLM | OpenAI GPT-4 |
| Deployment | Vercel / Render |

---

## **📊 Project Structure**

```
AI-TAX-REFORM/
├── frontend/          # Next.js React app
├── backend/           # FastAPI server  
├── data/              # Tax documents
├── scripts/           # Processing
├── graph/             # Neo4j schemas
├── DESIGNDOC.md       # Full design
├── TODO.txt           # Tasks
└── README.md          # This file
```

---

**Let's simplify Nigerian taxes! 🇳🇬✨**  
*Last Updated: November 27, 2025*