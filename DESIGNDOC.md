# Design Document: TaxMate – AI Tax Reform Assistant (Web First Approach)

**Prepared by:** Salaudeen Mubarak  
**Project:** Tax Reform Challenge 2025 – Student Submission  
**Date:** November 24, 2025

---

## **1. Project Overview**

### **Goal**
Develop a web-based RAG bot to help Nigerian students, NYSC participants, and citizens understand the 2025 Tax Reform Act. The bot leverages **Retrieval-Augmented Generation (RAG)** to provide accurate, contextual answers from official tax documents.

### **Objectives**

* Promote tax literacy among young Nigerians
* Simplify complex tax laws into plain language
* Test and validate functionality on a web platform before extending to WhatsApp
* Encourage community engagement and civic participation
* Provide a demo-ready product for the Tax Reform Challenge 2025

### **Target Audience**

* Undergraduate students across Nigerian universities
* NYSC participants
* Young entrepreneurs and first-time taxpayers
* Citizens seeking tax reform understanding

### **Tech Stack (Web-first)**

| Component | Technology |
|-----------|-----------|
| **Frontend** | React / Next.js |
| **Backend** | FastAPI / Flask |
| **LLM** | OpenAI GPT-4 / GPT-3.5 |
| **Embeddings** | OpenAI embeddings / HuggingFace |
| **Vector Database** | FAISS / Chroma / Pinecone |
| **Hosting** | Vercel / Render / Railway |
| **Real-time Communication** | WebSockets (optional, for live chat) |

---

## **2. System Architecture**

### **Web Flow Diagram**

```
[User Web Input] → [Message Processor] → [Vector DB Search] → [LLM Generator] → [Web UI Output]
                         ↓
                   [Query Validation]
                         ↓
                   [Relevance Filtering]
```

### **Core Components**

1. **Frontend Web App**
   - Input form or chat interface for user queries
   - Real-time message display
   - Responsive design for mobile and desktop
   - Optional voice input capability

2. **Backend API**
   - Receives user messages via REST or WebSocket endpoints
   - Handles RAG logic orchestration
   - Manages session and conversation history
   - Implements rate limiting and security

3. **Retriever Module**
   - Vector DB searches embedded tax documents
   - Returns top-K relevant chunks (default: top 5)
   - Implements relevance scoring and filtering

4. **Generator Module**
   - LLM synthesizes answers from retrieved context
   - Applies prompt templates for consistent outputs
   - Validates response quality before sending to user

5. **Vector Database**
   - Stores embeddings of tax reform documents
   - Enables semantic search for query-document matching
   - Supports efficient similarity search

### **Data Sources**

* 2025 Tax Reform Act PDF (primary)
* FIRS (Federal Inland Revenue Service) FAQs
* Government circulars and official guides
* Tax filing step-by-step documentation
* Policy clarification documents

### **Document Processing Pipeline**

```
PDF Upload
   ↓
[Extract Text]
   ↓
[Clean & Normalize]
   ↓
[Split into Chunks] (500-token chunks with overlap)
   ↓
[Generate Embeddings]
   ↓
[Store in Vector DB]
```

---

## **3. Features by Phase**

### **Phase 1 – Web MVP (Weeks 1-4)**

**Goal:** Launch a functional, demo-ready **web-based bot**.

**Features:**

* ✅ Text Q&A through web interface
* ✅ Context-aware answers from embedded official documents
* ✅ English language support
* ✅ Simple, responsive UI optimized for students
* ✅ Source citation (show which document was used)
* ✅ Error handling for unclear queries
* ✅ Basic conversation history

**Success Metrics:**

* Successfully retrieve and answer 10+ sample tax questions
* <2 second response time per query
* UI accessible on mobile and desktop
* Accuracy rate >85% on sample queries

**Demo Plan:**

* Live demo with 3–4 sample questions:
  * "What are the tax brackets under the 2025 reform?"
  * "How does NYSC affect my tax obligations?"
  * "What are the new deductions for students?"
* Show bot returning accurate answers with source references
* Highlight RAG retrieval process with transparency

---

### **Phase 2 – Web Enhanced Features (Weeks 5-8)**

**Goal:** Improve accessibility, interactivity, and usability.

**Features:**

* 🔄 Multi-language support (Hausa, Yoruba, Igbo)
* 🎤 Voice input on web (speech-to-text)
* 📊 Automatic law updates (document refresh mechanism)
* 📈 Analytics dashboard
  * Popular questions tracked
  * User engagement metrics
  * Query success rate
* 🎮 Gamified quizzes and mini-challenges
  * "Tax Reform Quiz" - test knowledge
  * Rewards/badges for learning milestones
* 📋 Step-by-step tax filing guidance
* 🔔 Event & seminar notifications
* 💬 Feedback collection system

**Success Metrics:**

* Support at least 3 local languages
* Voice accuracy >90%
* Quiz engagement from >30% of users
* Collect 500+ feedback entries

---

### **Phase 3 – Community & WhatsApp Integration (Weeks 9-12)**

**Goal:** Extend web bot to community features and WhatsApp platform.

**Features:**

* 👥 Community Q&A & feedback loop
  * User-submitted questions and answers
  * Community voting on helpfulness
* 🎁 Referral programs for engagement
  * Share quiz results
  * Invite friends with incentives
* 🤖 AI simplification of complex laws
  * Plain-language explanation generator
  * Analogy-based explanations
* 📱 Social media integration
  * Share insights on Twitter/LinkedIn
  * Social login for quick signup
* 📢 Push notifications for deadlines
  * Tax filing deadlines
  * New reforms announced
* 🎯 Scenario-based guidance
  * "I'm a student earning from freelance work" → personalized guide
  * "I'm planning to start a business" → entrepreneur tax guide
* 💬 **WhatsApp integration via Twilio or Meta API**
  * Same RAG bot accessible via WhatsApp
  * Message-based Q&A
  * Periodic tips and reminders
* 📚 Resource library
  * Downloadable guides and templates
  * Video tutorials
  * Success stories from taxpayers

**Impact Potential:**

* Significantly increased civic engagement
* Enhanced financial literacy across target demographics
* Potential for national adoption by tax authorities
* Foundation for future tax education platform

---

## **4. Web App UI/UX Design**

### **Layout Structure**

```
┌─────────────────────────────────────────────┐
│          Header: TaxMate Logo & Nav         │
├──────────────────┬──────────────────────────┤
│                  │                          │
│ FAQ/Tips Panel   │   Main Chat Window      │
│                  │   ┌────────────────────┐│
│ • Quick Links    │   │ Bot: "Hi, I'm...  ││
│ • Popular Qs     │   ├────────────────────┤│
│ • Glossary       │   │ User: "What are..." ││
│ • Resources      │   ├────────────────────┤│
│                  │   │ Bot: "According... ││
│                  │   │ [Source: Pg. 5]   ││
│                  │   ├────────────────────┤│
│                  │   │ Input box + Send   ││
│                  │   │ [🎤 Voice Input]   ││
│                  │   └────────────────────┘│
├──────────────────┴──────────────────────────┤
│  Footer: Analytics | Feedback | Settings   │
└─────────────────────────────────────────────┘
```

### **Key UI Components**

1. **Chat Window**
   - Message bubbles with timestamps
   - Bot responses with source citations
   - Typing indicators
   - Conversation history accessible

2. **FAQ/Quick Tips Panel**
   - Frequently asked questions
   - Quick tax tips
   - Glossary of tax terms
   - Links to official resources
   - Recent popular queries

3. **Input Area**
   - Text input field
   - Voice input button (Phase 2)
   - Send button
   - Character counter

4. **Analytics Dashboard** (Phase 2)
   - Queries answered today
   - User engagement metrics
   - Top questions
   - Language usage breakdown

### **Frontend Features**

* ✅ Fully responsive design (mobile-first)
* ✅ Accessibility-compliant (WCAG 2.1 AA)
* ✅ Clear color coding:
  * 🟢 Green for tips/positive info
  * 🔵 Blue for official references
  * 🟡 Yellow for warnings/important dates
* ✅ Dark/light mode toggle
* ✅ Optional voice input button
* ✅ Feedback button on each response
* ✅ Loading state with skeleton screens
* ✅ Error messages with suggested actions

### **Mobile Optimization**

* Bottom navigation for quick access
* Swipe gestures for navigation
* Large touch targets (48x48px minimum)
* Optimized images and lazy loading
* Progressive Web App (PWA) capability

---

## **5. RAG Implementation Details**

### **Retrieval Process**

1. **Query Embedding**
   - User query is converted to embeddings using OpenAI embeddings API
   - Query is normalized and cleaned

2. **Vector DB Search**
   - Similarity search against document embeddings
   - Returns top-5 relevant chunks
   - Applies relevance threshold (min cosine similarity: 0.7)

3. **Chunk Ranking**
   - Re-rank results by relevance score
   - Filter out low-confidence matches
   - Group related chunks for context

### **Generation Process**

1. **Context Assembly**
   - Combine top-K retrieved chunks with metadata
   - Maintain source references
   - Truncate if exceeds token limit

2. **Prompt Engineering**
   - System prompt establishes bot persona
   - Context injection with retrieved documents
   - Few-shot examples for consistency

3. **LLM Generation**
   - Stream response to user in real-time
   - Monitor for hallucinations
   - Validate response quality

### **Prompt Template**

```
System Prompt:
---
You are TaxMate, an AI assistant specialized in Nigerian Tax Reform 2025.
Your role is to help students, NYSC participants, and young professionals
understand the 2025 Tax Reform Act in simple, plain language.

Guidelines:
- Answer ONLY based on the provided official documents
- If uncertain, say "I don't have enough information"
- Break down complex concepts with examples
- Always cite the source document
- Keep responses concise and actionable
- Use bullet points for clarity
- Avoid speculation or unofficial interpretations
---

Context from Official Documents:
{retrieved_documents}

User Query:
{user_query}

Answer:
```

### **Quality Assurance**

* Response validation against source documents
* Confidence scoring on generated answers
* Manual review of edge cases
* User feedback loop for continuous improvement
* Regular accuracy audits

---

## **6. Data Security & Privacy**

* **User Data**
  - Minimal collection (optional name, email)
  - GDPR/NDPR compliant data handling
  - Encrypted transmission (HTTPS)
  - No personal financial information stored

* **Document Security**
  - Source documents stored securely
  - Access logs maintained
  - Regular backups

* **API Security**
  - Rate limiting per IP/user
  - API key management
  - Input validation and sanitization
  - CORS configuration for web origin only

---

## **7. Deployment & Infrastructure**

### **Web Hosting Options**

| Platform | Pros | Cons |
|----------|------|------|
| **Vercel** | Fast, seamless Next.js deployment | Requires paid plan for high traffic |
| **Render** | Free tier available, easy deployment | Cold starts can be slow |
| **Railway** | Good pricing, simple setup | Smaller community |

### **Backend Hosting**

* **FastAPI** deployed on Railway or Render
* **Environment variables** for API keys (OpenAI, Pinecone, etc.)
* **Database** hosted on Railway PostgreSQL or similar
* **Vector DB** on Pinecone (managed) or self-hosted FAISS

### **CI/CD Pipeline**

* GitHub Actions for automated testing
* Automated deployment on push to `main`
* Staging environment for testing
* Rollback capability

---

## **8. Success Metrics & KPIs**

### **Phase 1 (MVP)**

| Metric | Target |
|--------|--------|
| Questions answered accurately | >85% |
| Average response time | <2 seconds |
| Mobile accessibility score | >95 |
| Uptime | 99.5% |

### **Phase 2**

| Metric | Target |
|--------|--------|
| Monthly active users | 1,000+ |
| Quiz completion rate | 30%+ |
| User satisfaction (NPS) | >50 |
| Multi-language coverage | 3+ languages |

### **Phase 3**

| Metric | Target |
|--------|--------|
| WhatsApp users | 5,000+ |
| Community contributions | 200+ answers |
| Referral rate | 20%+ |
| National media mentions | 5+ |

---

## **9. Development Roadmap**

### **Timeline Overview**

```
Week 1-2: Setup & Documentation Processing
├── Project setup (React + FastAPI)
├── Document ingestion pipeline
└── Vector DB initialization

Week 3-4: Core RAG Implementation
├── Retrieval module
├── LLM integration
└── Web UI development

Week 5: Testing & MVP Demo
├── End-to-end testing
├── Performance optimization
└── Tax Reform Challenge submission

Week 6-8: Phase 2 Features
├── Multi-language support
├── Voice input integration
├── Analytics dashboard
└── Gamification features

Week 9-12: Phase 3 & Scaling
├── Community features
├── WhatsApp integration
├── Scale infrastructure
└── Launch updates & notifications
```

### **Milestone Checklist**

- [ ] Week 1: Development environment ready
- [ ] Week 2: Tax documents processed and embedded
- [ ] Week 3: Retrieval module functional
- [ ] Week 4: LLM integration complete
- [ ] Week 5: MVP web app deployed
- [ ] Week 5-End: Tax Reform Challenge demo
- [ ] Week 6: Multi-language support
- [ ] Week 8: Analytics dashboard live
- [ ] Week 12: WhatsApp integration ready

---

## **10. Risk Mitigation**

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **LLM hallucinations** | Misinformation | Strict prompt engineering + source validation |
| **High API costs** | Budget overrun | Rate limiting, caching, usage monitoring |
| **Vector DB latency** | Poor UX | Implement caching, optimize chunk size |
| **Document updates** | Outdated info | Monthly refresh cycle, version tracking |
| **Low user adoption** | Project failure | Early marketing, university partnerships |
| **Tax law changes** | Information drift | Regular document audits, changelog system |

---

## **11. Future Enhancements (Post-Phase 3)**

* 🤖 AI-powered tax calculator
* 📱 Mobile app (iOS/Android)
* 🌐 Marketplace for tax professionals
* 📊 Investment in tax planning tool
* 🎓 Certificate program for tax literacy
* 🔗 Integration with FIRS portal
* 🏢 B2B version for organizations

---

## **12. Budget Estimate (3 Months)**

| Component | Estimated Cost |
|-----------|----------------|
| **Cloud Hosting** | $200-500 |
| **OpenAI API** | $300-800 |
| **Vector DB (Pinecone)** | $100-300 |
| **Domain & SSL** | $50-100 |
| **Development Tools** | $50-100 |
| **Miscellaneous** | $100 |
| **TOTAL** | ~$800-1,800 |

*Note: Costs scale with usage in Phase 2-3*

---

## **13. Contact & Support**

**Project Lead:** Salaudeen Mubarak  
**Repository:** https://github.com/Mozzicato/AI-TAX-REFORM  
**Email:** [contact email]  

**Key Stakeholders:**
* Tax Reform Challenge 2025 organizers
* Nigerian university student associations
* NYSC representatives
* FIRS communication team

---

## **Appendix: Glossary**

* **RAG** - Retrieval-Augmented Generation
* **LLM** - Large Language Model
* **FAISS** - Facebook AI Similarity Search
* **Vector DB** - Vector Database for embeddings
* **Embeddings** - Numerical representations of text
* **Prompt Engineering** - Crafting effective LLM prompts
* **NPS** - Net Promoter Score
* **NYSC** - National Youth Service Corps
* **FIRS** - Federal Inland Revenue Service
* **PWA** - Progressive Web App

---

**Document Version:** 1.0  
**Last Updated:** November 24, 2025  
**Status:** Approved for Development
