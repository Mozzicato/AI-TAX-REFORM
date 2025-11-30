---
title: NTRIA - Nigeria Tax Reform Intelligence Assistant
emoji: 🇳🇬
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 4.26.0
app_file: app.py
pinned: true
license: mit
---

# 🇳🇬 NTRIA - Nigeria Tax Reform Intelligence Assistant

A sophisticated AI-powered assistant that helps Nigerians understand and navigate the 2025 Tax Reform Act using Graph-Enhanced Retrieval-Augmented Generation (Graph RAG).

## Features

- **📚 Comprehensive Tax Guidance**: Get accurate information about Nigeria's tax obligations, brackets, and compliance requirements
- **🔗 Knowledge Graph**: Advanced knowledge graph connecting tax concepts, regulations, and compliance procedures
- **💡 Personalized Recommendations**: Receive tailored advice based on your specific tax situation
- **📋 Compliance Alerts**: Stay informed about important tax deadlines and requirements
- **🎯 Multi-step Guidance**: Navigate complex tax scenarios with step-by-step explanations

## How to Use

1. **Ask a Question**: Type your tax-related question in the text box
2. **Get Instant Response**: Receive AI-generated answers with citations from official documents
3. **View Sources**: See the official documents and sources used to generate each response
4. **Clear & Continue**: Clear chat history and ask follow-up questions

## Example Questions

- What are the new tax brackets under the 2025 reform?
- Who is eligible for tax reliefs in Nigeria?
- What are the compliance deadlines for the new tax year?
- How does the simplified taxation for small businesses work?
- What documents do I need for tax registration?

## Technology Stack

- **Frontend**: Gradio (Python UI framework)
- **Backend**: FastAPI with Graph RAG Pipeline
- **Knowledge Base**: Neo4j Graph Database
- **Vector Store**: Pinecone for semantic search
- **LLM**: OpenAI GPT models
- **Document Processing**: Advanced NLP and PDF extraction

## About

**NTRIA** is built to make Nigeria's tax system more accessible and understandable to students, entrepreneurs, NYSC participants, and citizens. By combining advanced AI with official tax documentation, we provide reliable, up-to-date tax guidance.

## Disclaimer

This assistant is designed for informational purposes only. While it strives to provide accurate information based on the 2025 Tax Reform Act, it should not be used as a substitute for professional tax advice. For critical tax decisions, please consult with qualified tax professionals and accountants.

## Data Sources

- Nigeria 2025 Tax Reform Act (Official Documents)
- Nigerian Revenue Service (NRS) Guidelines
- Federal Inland Revenue Service (FIRS) Publications

---

**Status**: ✅ Live on Hugging Face Spaces  
**Built with**: Gradio + Graph RAG  
**License**: MIT