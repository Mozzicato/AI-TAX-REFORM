# 📘 Design Document: Graph RAG System – Nigeria Tax Reform Intelligence Bot (NTRIA)

**Author:** Salaudeen Mubarak  
**Product:** Nigeria Tax Reform Intelligence Assistant (NTRIA)  
**Architecture:** Graph RAG + LLM Reasoning Engine  
**Deployment Phases:** 3 phases (Web → Enhanced Web → WhatsApp Integration)  
**Date:** November 27, 2025  
**Project:** Tax Reform Challenge 2025 – Student Submission

---

## **PHASE 1: WEB-BASED GRAPH RAG BOT (MVP)**

This phase focuses on launching the intelligent web assistant using Graph RAG.

---

## **1. System Overview**

### **1.1 Product Definition**

**NTRIA** is an intelligent advisory assistant that explains, navigates, and interprets the **Nigeria Tax Reform Act 2025** using a **Graph-enhanced Retrieval-Augmented Generation (Graph RAG)** architecture.

Unlike traditional RAG, Graph RAG builds a structured **knowledge graph** of the tax ecosystem, enabling deeper reasoning and accurate multi-step responses.

### **1.2 Core Objectives**

* Provide **factual**, **context-aware**, and **accurate** interpretation of tax laws using graph-enhanced reasoning
* Improve national **tax literacy** and **youth engagement**
* Support policymakers with **structured insights** from citizen interactions
* Enable accurate **multi-step tax compliance** guidance
* Simplify complex tax laws into plain language
* Serve as an educational and advisory channel for students, SMEs, and citizens
* Provide a demo-ready product for the Tax Reform Challenge 2025

### **1.3 Target Audience**

* Undergraduate students across Nigerian universities
* NYSC participants
* Young entrepreneurs and first-time taxpayers
* Citizens seeking tax reform understanding

### **1.4 Success Criteria (MVP)**

* Successfully answer 10+ sample tax questions with >85% accuracy
* Response time <2 seconds per query
* Mobile and desktop accessibility
* Source citations on all responses
* Functional web demo deployment

---

## **2. Graph RAG Architecture Overview**

### **2.1 What is Graph RAG?**

Graph RAG enhances traditional RAG by building a **structured knowledge graph** of relationships between tax concepts, rules, and entities. This enables:

* **Deeper reasoning** across multi-step tax processes
* **Better context** through entity relationships
* **Reduced hallucinations** through enforced graph constraints
* **Improved multi-hop** query resolution
* **Knowledge organization** that mirrors actual tax complexity

### **2.2 High-Level System Flow**

```
┌──────────────────────────────────────────────────────────────┐
│                       USER QUERY                             │
│          "What are my tax obligations as a freelancer?"      │
└────────────────────────┬─────────────────────────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │   Query Understanding Engine    │
        │   - Extract: Freelancer, Tax    │
        │   - Intent: Compliance check    │
        └────────────────┬────────────────┘
                         │
     ┌───────────────────▼──────────────────┐
     │   Graph Traversal & Retrieval        │
     │   - Find: Freelancer node            │
     │   - Traverse: liable_for edges       │
     │   - Collect: All applicable taxes    │
     └───────────────────┬──────────────────┘
                         │
      ┌──────────────────▼──────────────────┐
      │   Subgraph Assembly                 │
      │   - Collect tax details             │
      │   - Add thresholds & deadlines      │
      │   - Include exemptions              │
      └──────────────────┬──────────────────┘
                         │
       ┌─────────────────▼──────────────────┐
       │   LLM Response Generation          │
       │   - Context + Query → Response     │
       │   - Add source citations           │
       │   - Format for clarity             │
       └─────────────────┬──────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │   RESPONSE TO USER              │
        │   Formatted answer with sources │
        └────────────────────────────────┘
```

### **2.3 Architecture Components**

```
┌────────────────────────────────────────────────────────────┐
│                   FRONTEND LAYER                           │
│  React/Next.js Chat Interface, Mobile-Optimized UI         │
└────────────┬───────────────────────────────────┬───────────┘
             │                                   │
┌────────────▼────────────┐      ┌───────────────▼────────────┐
│   API Gateway           │      │   WebSocket Handler        │
│   REST Endpoints        │      │   Real-time Messages       │
└────────────┬────────────┘      └───────────────┬────────────┘
             │                                   │
┌────────────▼──────────────────────────────────▼────────────┐
│                 BACKEND ORCHESTRATION LAYER                │
│              FastAPI / Node.js Application                 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────┐    ┌──────────────────────┐        │
│  │ Query Parser     │    │ Intent Classifier    │        │
│  │ Entity Extractor │    │ Validation Engine    │        │
│  └────────┬─────────┘    └──────────┬───────────┘        │
│           │                         │                    │
│  ┌────────▼─────────────────────────▼────────┐           │
│  │    Graph RAG Pipeline Engine               │           │
│  │  - Graph Query Generation (Cypher)        │           │
│  │  - Semantic Search (Vector DB)            │           │
│  │  - Hybrid Result Fusion                   │           │
│  └────────┬─────────────────────────────────┘            │
│           │                                              │
└───────────┼──────────────────────────────────────────────┘
            │
    ┌───────┴─────────────────────────────────┐
    │                                         │
┌───▼──────────────────┐    ┌─────────────────▼──────────────┐
│  Neo4j Knowledge     │    │  Vector Database              │
│  Graph Database      │    │  (FAISS/Chroma/Pinecone)     │
├──────────────────────┤    ├───────────────────────────────┤
│ • Tax Nodes          │    │ • Doc Embeddings             │
│ • Entity Relations   │    │ • Semantic Search            │
│ • Rules/Policies     │    │ • Similarity Ranking         │
│ • Multi-hop Queries  │    │ • Hybrid Search Support      │
└──────────────────────┘    └──────────────────────────────┘
    │
┌───▼────────────────────────────────────────────────────┐
│  LLM Response Generation                              │
│  (OpenAI GPT-4 / DeepSeek / Groq)                    │
├────────────────────────────────────────────────────────┤
│ • Receive: Graph Context + User Query                │
│ • Process: Chain-of-thought Reasoning                │
│ • Output: Human-readable Response                    │
│ • Validate: Hallucination Check                      │
└────────────────────────────────────────────────────────┘
```

### **2.4 Tech Stack (Graph RAG Architecture)**

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Frontend** | React / Next.js | Fast, interactive UI with SSR |
| **Backend** | FastAPI | High performance, async support |
| **Knowledge Graph DB** | Neo4j | Industry standard, powerful Cypher queries |
| **Vector Database** | Pinecone / Chroma | Semantic search, hybrid with graphs |
| **LLM** | OpenAI GPT-4 | Accurate reasoning, entity extraction |
| **Embeddings** | OpenAI / HuggingFace | High-quality semantic representations |
| **Entity Extraction** | GPT-4 + Spacy | Accurate extraction from tax documents |
| **Graph Framework** | LangChain / Microsoft GraphRAG | Orchestrates RAG pipeline |
| **Frontend Hosting** | Vercel | Automatic deployments, CDN |
| **Backend Hosting** | Render / Railway | Cost-effective, Python-friendly |

---

## **3. Knowledge Graph Schema & Design**

### **3.1 Node Types**

```
(Tax {
  type: "VAT" | "PAYE" | "CGT" | "DST" | "Education Tax",
  rate: "7.5%",
  effective_date: "2025-01-01",
  description: "Full description"
})

(Taxpayer {
  category: "Individual" | "Freelancer" | "SME" | "Digital Service Provider",
  resident: true|false,
  annual_turnover_threshold: 25000000,
  compliance_level: "Basic" | "Intermediate" | "Advanced"
})

(Agency {
  name: "FIRS" | "JTB" | "State IRS",
  jurisdiction: "Federal" | "State",
  contact: "email@address.com"
})

(Process {
  name: "VAT Registration" | "PAYE Filing" | "Annual Return",
  duration: "5-7 days",
  documentation: ["Doc1", "Doc2"],
  frequency: "Annual" | "Quarterly" | "Monthly"
})

(Threshold {
  amount: 25000000,
  currency: "NGN",
  applies_to: "Annual Turnover" | "Monthly Income",
  logic: "above|below"
})

(Penalty {
  type: "Late Filing" | "Non-payment" | "Under-reporting",
  amount: 50000,
  percentage: "5%",
  calculation_basis: "Tax Amount"
})

(Deadline {
  event: "Annual PAYE Return",
  date: "2025-03-31",
  frequency: "Annual" | "Quarterly" | "Monthly",
  days_before_reminder: 14
})

(Rule {
  content: "Digital services attract 5% DST",
  policy_ref: "Tax Reform Act Section 7",
  effective_date: "2025-01-01",
  status: "Active" | "Archived"
})

(Document {
  title: "2025 Tax Reform Act",
  source: "FIRS",
  pages: 145,
  upload_date: "2025-01-01",
  version: "1.0"
})

(Exception {
  description: "Exemption for education services",
  applies_to: "Education sector",
  conditions: "Non-profit entities only"
})
```

### **3.2 Relationship Types**

```
(Tax) —[applies_to]→ (Taxpayer)
  Properties: {condition: "if annual_turnover > threshold"}

(Tax) —[enforced_by]→ (Agency)
  Properties: {since: "2025-01-01"}

(Tax) —[requires]→ (Process)
  Properties: {mandatory: true}

(Process) —[defined_in]→ (Document)
  Properties: {section: 5, page: 12}

(Taxpayer) —[liable_for]→ (Tax)
  Properties: {status: "Active"}

(Threshold) —[triggers]→ (Tax)
  Properties: {logic: "above"}

(Penalty) —[applies_to]→ (Tax)
  Properties: {condition: "Late payment"}

(Deadline) —[applies_to]→ (Process)
  Properties: {days_before_reminder: 14}

(Rule) —[exempts]→ (Taxpayer)
  Properties: {condition: "Non-profit"}

(Rule) —[overrides]→ (Rule)
  Properties: {reason: "Newer regulation"}

(Tax) —[has_exception]→ (Exception)
  Properties: {}
```

### **3.3 Example Knowledge Graph**

**Query:** "What are tax obligations for a digital service provider earning ₦50M annually?"

**Graph Traversal:**

```
[Digital Service Provider]
        ↓ (liable_for)
[VAT Tax]     [DST Tax]     [PAYE Tax]
        ↓           ↓            ↓
[7.5% rate]  [5% rate]   [21% band]
        ↓           ↓            ↓
[Quarterly] [Quarterly] [Monthly]
  Filing      Filing      Filing
        ↓           ↓            ↓
[March 31]  [March 31] [10th of month]
  Deadline    Deadline   Deadline
        ↓           ↓            ↓
[Penalty]   [Penalty]  [Penalty]
[5% + Fees] [2.5%]     [Interest+Fees]
```

### **3.4 Neo4j Cypher Queries**

**Query 1: Get all applicable taxes for a taxpayer type**
```cypher
MATCH (t:Taxpayer {category: "Digital Service Provider"})-[r:liable_for]->(tax:Tax)
RETURN tax.type, tax.rate, tax.description
ORDER BY tax.type
```

**Query 2: Multi-hop query - Tax → Process → Deadline**
```cypher
MATCH (t:Taxpayer {category: "Freelancer"})-[:liable_for]->(tax:Tax)
      -[:requires]->(proc:Process)-[:applies_to]->(deadline:Deadline)
WHERE deadline.date > date()
RETURN tax.type, proc.name, deadline.date
ORDER BY deadline.date
```

**Query 3: Get exemptions and exceptions**
```cypher
MATCH (tp:Taxpayer {category: "Education Sector"})-[:subject_to]->(tax:Tax),
      (tax)-[:has_exception]->(exc:Exception)
RETURN tax.type, exc.description
```

**Query 4: Penalty information flow**
```cypher
MATCH (tp:Taxpayer {category: "SME"})-[:liable_for]->(tax:Tax)-[:applies_to]-(penalty:Penalty)
RETURN tax.type, penalty.type, penalty.amount, penalty.percentage
```

---

## **4. Graph RAG Implementation Pipeline**

### **4.1 Document Ingestion & Processing**

**Step 1: Document Collection**
- Upload PDF: 2025 Tax Reform Act
- Collect FIRS FAQs, circulars, guidelines
- Extract text using PyPDF2 or pdfplumber

**Step 2: Text Preprocessing**
```
Raw PDF Text
    ↓
[Clean & Normalize] (remove headers, footers)
    ↓
[Sentence Tokenization]
    ↓
[Split into Chunks] (500-token chunks with 50-token overlap)
    ↓
[Add Metadata] (source, page, section)
```

**Step 3: Entity & Relationship Extraction**
```
For each chunk:
  1. Send to GPT-4 with prompt:
     "Extract tax entities (types, bodies, taxpayers, penalties)
      and relationships (applies_to, enforced_by, etc.)"
  
  2. Parse structured output
  
  3. Create Neo4j nodes and relationships
```

**Step 4: Embedding Generation**
- Generate embeddings for all chunks (OpenAI embedding model)
- Store in vector database (Pinecone/Chroma)
- Create indices for fast retrieval

**Step 5: Graph Database Population**
- Insert extracted entities as nodes
- Create relationships between entities
- Build graph indices for query optimization

### **4.2 Query Processing Pipeline**

**Step 1: Query Understanding**
```
User Input: "What taxes do freelancers pay?"
    ↓
[Tokenize & Clean]
    ↓
[Extract Entities] → ["Freelancer", "Tax"]
    ↓
[Classify Intent] → "Tax Obligation Query"
    ↓
[Generate Entity Filter] → {category: "Freelancer", entity_type: "Tax"}
```

**Step 2: Graph Query Generation**
```
Entities: {category: "Freelancer"}
Intent: "Get all applicable taxes"
    ↓
Generate Cypher:
  MATCH (t:Taxpayer {category: "Freelancer"})-[:liable_for]->(tax:Tax)
  RETURN tax
```

**Step 3: Hybrid Retrieval**

**Graph Search:**
- Execute Cypher query on Neo4j
- Retrieve: Tax nodes, rates, processes, deadlines, penalties

**Vector Search:**
- Convert query to embedding
- Search vector database for similar chunks
- Retrieve: Top-5 most relevant document sections

**Fusion:**
- Combine graph results with vector results
- De-duplicate information
- Rank by relevance score

**Step 4: Context Assembly**
```
Graph Results: [VAT 7.5%, DST 5%, PAYE 21%]
Vector Results: [Relevant doc chunks about each tax]
    ↓
Structured Context:
{
  "primary_taxes": [VAT, DST, PAYE],
  "details": {...},
  "sources": [...],
  "deadlines": [...],
  "penalties": [...]
}
```

**Step 5: LLM Response Generation**
```
Prompt Template:
---
You are NTRIA, an expert on Nigeria Tax Reform 2025.

Context from Knowledge Graph:
{structured_context}

User Query: {query}

Instructions:
- Answer based ONLY on provided context
- If uncertain, say "I don't have complete information"
- Cite source documents
- Use simple, clear language
- Provide actionable next steps

Answer:
```

**Step 6: Response Validation**
- Check for hallucinations
- Verify citations against source docs
- Validate accuracy
- Add confidence score

### **4.3 Example Query Flow**

**User Query:** "I'm a freelancer earning ₦2M annually. What are my tax obligations?"

**Processing:**

1. **Entity Extraction**
   - Taxpayer: Freelancer
   - Income: ₦2M
   - Query Type: Compliance Check

2. **Graph Traversal**
   ```cypher
   MATCH (f:Freelancer)-[:liable_for]->(taxes:Tax)
         -[:requires]->(proc:Process)
         -[:applies_to]->(deadline:Deadline)
   RETURN taxes, proc, deadline
   ```
   Result: VAT (if threshold met), PAYE, Education Tax

3. **Context Retrieval**
   - VAT threshold: ₦25M (not applicable)
   - PAYE bands and rates for income ₦2M
   - Education tax: 1% of gross
   - Filing deadlines and processes

4. **LLM Response**
   ```
   As a freelancer with ₦2M annual income, here are your tax obligations:
   
   1. PAYE Tax
      - Applicable: No (below ₦8M threshold for individuals)
      - Amount: ₦0
   
   2. Education Tax
      - Applicable: Yes
      - Rate: 1% of gross income
      - Amount: ₦20,000 annually
   
   3. VAT
      - Applicable: No (turnover below ₦25M)
   
   4. Filing Requirements
      - Submit quarterly income tax declaration
      - Maintain tax records for 6 years
      - Register for tax identification number (TIN)
   
   Sources: Tax Reform Act 2025, Sections 3-7; FIRS Guidelines
   ```

---

## **5. Web MVP Features**

### **5.1 Core Features (Phase 1)**

**Chat Interface**
- Text-based Q&A
- Conversation history
- Source citations on every response
- Real-time typing indicators
- Mobile-responsive design

**Tax Knowledge Base**
- Answers 10+ sample tax questions with >85% accuracy
- Multi-step compliance guidance
- Deadline alerts
- Penalty information

**User Experience**
- Clean, intuitive interface
- FAQ quick-link panel
- Glossary of tax terms
- Sample questions for exploration

### **5.2 UI Layout**

```
┌──────────────────────────────────────────────────┐
│  NTRIA - Nigeria Tax Reform Intelligence Bot     │
│  [Home] [About] [FAQ] [Contact]                  │
├─────────────────┬────────────────────────────────┤
│                 │                                │
│  Quick Links    │    Chat Window                 │
│  ────────────   │    ──────────────              │
│  • PAYE FAQ     │    ┌──────────────────────┐    │
│  • VAT Guide    │    │ Bot: Hi! I'm NTRIA.  │    │
│  • DST Info     │    │ How can I help?      │    │
│  • Deadlines    │    ├──────────────────────┤    │
│  • Glossary     │    │ User: Am I liable... │    │
│                 │    ├──────────────────────┤    │
│  Popular Qs     │    │ Bot: Based on the... │    │
│  ────────────   │    │ [Source: Tax Act]    │    │
│  • VAT 101      │    ├──────────────────────┤    │
│  • Filing Tips  │    │ [Input field]        │    │
│  • Penalties    │    │ [Send] [Voice]       │    │
│                 │    └──────────────────────┘    │
├─────────────────┴────────────────────────────────┤
│  Footer: Privacy | Terms | Feedback              │
└──────────────────────────────────────────────────┘
```

---

## **6. Backend API Specification**

### **6.1 Key Endpoints**

**POST /api/v1/chat**
```json
Request:
{
  "message": "What taxes do freelancers pay?",
  "session_id": "user123",
  "context": {
    "taxpayer_type": "Freelancer",
    "income": 2000000
  }
}

Response:
{
  "response": "As a freelancer with...",
  "sources": [
    {"title": "Tax Reform Act", "section": 3, "page": 12},
    {"title": "FIRS FAQ", "section": "Freelancers"}
  ],
  "confidence": 0.95,
  "graph_path": [
    {"node": "Freelancer", "relation": "liable_for", "next": "Tax"}
  ]
}
```

**GET /api/v1/graph/entities**
```
Returns all entities of a type (Tax, Taxpayer, etc.)
Useful for autocomplete in UI
```

**POST /api/v1/graph/search**
```
Custom graph query endpoint
Allows complex searches using structured queries
```

**GET /api/v1/analytics**
```
Returns usage analytics (popular questions, etc.)
For judges/stakeholders to see impact
```

---

## **PHASE 2: ENHANCED WEB FEATURES**

---

## **7. Advanced Features (Phase 2 – Weeks 5-8)**

### **7.1 Citizen Tax Health Checker**

Users answer questionnaire → Bot assesses:
- Current compliance status
- Potential tax liabilities
- Risk areas (penalties, deadlines missed)
- Personalized recommendations

### **7.2 SME Tax Advisor**

Industry-specific guidance:
- Tech startups
- Food/hospitality vendors
- Freelancers and consultants
- Transport/logistics companies
- E-commerce businesses

### **7.3 Interactive Tax Calculator**

- Income tax calculation
- VAT computation
- Estimated penalties
- Filing fee estimates

### **7.4 Policy Simulator**

Scenario planning:
- "What if VAT increases to 8%?"
- "What if DST expands?"
- Impact estimation on different taxpayer types

### **7.5 Tax Literacy Gamification**

- Quiz mode with multiple choice
- Achievement badges
- Leaderboard
- Streak tracking

### **7.6 Multilingual Support**

- Pidgin English
- Yoruba
- Hausa
- Igbo

### **7.7 Analytics Dashboard**

Insights for policymakers:
- Most confusing tax concepts
- Common citizen questions
- Compliance pattern analysis
- Regional breakdown

### **7.8 Nigerian Tax Calendar**

Automated reminders:
- VAT filing deadlines (Quarterly)
- PAYE submission (Monthly)
- Annual returns (End of fiscal year)
- Special compliance dates

---

## **PHASE 3: WHATSAPP INTEGRATION**

---

## **8. WhatsApp Bot Architecture**

### **8.1 Integration Overview**

After Phase 1 web bot is stable, extend to WhatsApp using Meta's Business API or Twilio.

**Architecture:**

```
WhatsApp User
    ↓
[WhatsApp Business API / Twilio]
    ↓
[Webhook Receiver]
    ↓
[Message Parser & Intent Classifier]
    ↓
[Graph RAG Pipeline] (same as web)
    ↓
[Response Formatter for WhatsApp]
    ↓
[Send Back via API]
    ↓
WhatsApp User
```

### **8.2 WhatsApp Features**

**Text Q&A**
- Same Graph RAG intelligence
- Natural language understanding
- Multi-turn conversations

**Quick Reply Menus**
- "1. Check Tax Obligations"
- "2. Filing Deadlines"
- "3. Penalty Information"

**Media Sharing**
- PDF summaries of responses
- Tax calendar downloads
- Guidance documents

**Automation**
- Deadline reminders
- Tax tips (daily/weekly)
- News on tax changes

**Voice Support**
- "Send voice message → transcription → answer"
- For users with low literacy

---

## **9. Future Enhancements**

### **9.1 NIN/CAC Integration** (Post-Phase 3)

With user consent:
- Verify business type via CAC
- Auto-detect applicable taxes
- Personalized compliance guidance

### **9.2 Agentic Tax Filing Support** (2026+)

LLM agents that can:
- Auto-fill tax forms
- Compute VAT amounts
- Generate PAYE schedules
- Check penalty calculations

### **9.3 Community Feedback Loop**

Citizens can anonymously report:
- Unfair tax practices
- Corruption issues
- Double taxation cases
- Knowledge gaps

Graph updated based on patterns.

### **9.4 Tax Advisory Marketplace**

Connect users with:
- Certified tax consultants
- Accountants
- Compliance officers

### **9.5 Voice Tax Assistant (IVR)**

For rural & low-literacy users:
- "Press 1 for VAT guidance"
- "Press 2 to report issues"
- Automated voice responses

### **9.6 Revenue Prediction Engine**

For government strategic planning:
- Behavioral data analysis
- Compliance pattern prediction
- MSME growth tracking

### **9.7 Bank/Fintech Plugin API**

Banks embed NTRIA in:
- Mobile banking apps
- SME dashboards
- Loan pre-qualification tools

### **9.8 Regional Tax Authority Integration**

Connect State IRSs to:
- Distribute state-specific guidance
- Track state tax compliance
- Support state revenue targets

---

## **10. Deployment & Infrastructure**

### **10.1 Hosting Architecture**

**Frontend (Vercel)**
- Next.js deployment
- Automatic CI/CD
- CDN for global distribution
- Cost: $20-50/month

**Backend (Render / Railway)**
- FastAPI on Python runtime
- PostgreSQL for sessions/logs
- Auto-scaling with traffic
- Cost: $50-100/month

**Knowledge Graph (Neo4j)**
- Managed Neo4j cloud instance
- Backup and replication
- Query optimization
- Cost: $100-200/month

**Vector DB (Pinecone)**
- Serverless embeddings storage
- API-based access
- Auto-scaling
- Cost: $50-100/month

**LLM API (OpenAI)**
- Pay-per-token
- Rate limiting ($20-30 daily during testing)
- Upgrade based on usage

### **10.2 CI/CD Pipeline**

```
GitHub Push
    ↓
[Run Tests]
    ↓
[Build Docker Image]
    ↓
[Deploy to Staging]
    ↓
[Integration Tests]
    ↓
[Deploy to Production]
    ↓
[Monitor & Alert]
```

### **10.3 Security Measures**

* HTTPS/TLS for all traffic
* Rate limiting per IP/user
* Input validation and sanitization
* XSS/CSRF protection
* Audit logs for all queries
* GDPR/NDPR compliance
* Data encryption at rest

---

## **11. Success Metrics & KPIs**

### **Phase 1 (MVP)**

| Metric | Target |
|--------|--------|
| Questions answered accurately | >85% |
| Average response time | <2 seconds |
| Mobile accessibility score | >95 |
| Uptime | 99.5% |
| Graph query accuracy | >90% |

### **Phase 2**

| Metric | Target |
|--------|--------|
| Monthly active users | 1,000+ |
| Quiz completion rate | 30%+ |
| User satisfaction (NPS) | >50 |
| Languages supported | 4+ |
| Daily API calls | 10,000+ |

### **Phase 3**

| Metric | Target |
|--------|--------|
| WhatsApp users | 5,000+ |
| Community contributions | 200+ answers |
| Referral rate | 20%+ |
| Media coverage | 5+ mentions |
| Government interest | FIRS integration discussions |

---

## **12. Development Roadmap**

### **Timeline**

```
Week 1-2: Setup & Graph Design
├── Project initialization
├── Neo4j database setup
└── Document collection & preprocessing

Week 3-4: Graph Population & Backend
├── Entity extraction pipeline
├── Neo4j population
├── FastAPI backend development
└── Hybrid retrieval implementation

Week 5: Frontend & Integration
├── React/Next.js UI build
├── API integration
├── End-to-end testing
└── Performance optimization

Week 6-8: Phase 2 Features
├── Multi-language support
├── Analytics dashboard
├── Gamification
└── Additional AI features

Week 9-12: WhatsApp & Polish
├── Twilio integration
├── WhatsApp testing
├── Scale infrastructure
└── Final deployment
```

### **Key Milestones**

- [ ] Week 1: Neo4j + document pipeline ready
- [ ] Week 2: First entities extracted to graph
- [ ] Week 3: Backend Graph RAG working
- [ ] Week 4: FastAPI endpoints functional
- [ ] Week 5: Frontend UI deployed
- [ ] Week 5-End: MVP demo + Tax Reform Challenge submission
- [ ] Week 6: Multi-language operational
- [ ] Week 8: Full Phase 2 feature set
- [ ] Week 12: WhatsApp bot live

---

## **13. Deliverables for Competition**

### **What You Will Present**

1. **Architecture Diagram**
   - Component flow (Frontend → Backend → Graph → LLM)
   - Data pipeline visualization
   - System interactions

2. **Knowledge Graph Schema Diagram**
   - Node types with properties
   - Relationship types
   - Sample subgraph

3. **End-to-End Pipeline Diagram**
   - Document ingestion → Entity extraction → Graph population
   - Query processing → Graph traversal → LLM generation

4. **Live Web Prototype**
   - Functional chat interface
   - 3-4 demo questions answered
   - Source citations shown

5. **Demo Video** (2-3 minutes)
   - Show UI and features
   - Live question answered
   - Graph visualization (if available)

6. **Executive Summary** (1-2 pages)
   - Problem statement
   - Solution overview
   - Why Graph RAG is superior
   - Impact potential

7. **Technical Documentation**
   - Setup instructions
   - API documentation
   - Graph schema details

---

## **14. Risk Mitigation**

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **LLM hallucinations** | Misinformation | Graph validation, confidence scoring, manual review |
| **Graph complexity** | Performance issues | Query optimization, caching, incremental updates |
| **High API costs** | Budget overrun | Rate limiting, caching, prompt optimization |
| **Tax document updates** | Information drift | Monthly refresh schedule, versioning system |
| **User adoption** | Low engagement | Marketing, university partnerships, gamification |
| **Integration delays** | Timeline slip | Modular design, parallel development |

---

## **15. Budget Estimate (12 Weeks)**

| Component | Monthly | 3 Months |
|-----------|---------|----------|
| Cloud Hosting (Render) | $75 | $225 |
| Neo4j Cloud | $150 | $450 |
| Pinecone Vector DB | $75 | $225 |
| OpenAI API | $30-50 | $100-150 |
| Domain & SSL | $5 | $15 |
| **TOTAL** | **$335-385** | **~$1,000-1,100** |

*Note: Costs scale with usage in Phase 2-3*

---

## **16. Glossary**

* **Graph RAG** - Retrieval-Augmented Generation enhanced with knowledge graphs
* **Neo4j** - Graph database for storing relationships
* **Cypher** - Query language for Neo4j
* **Embeddings** - Vector representations of text
* **Multi-hop** - Query that traverses multiple relationship steps
* **LLM** - Large Language Model (like GPT-4)
* **NIN** - National Identification Number
* **CAC** - Corporate Affairs Commission
* **FIRS** - Federal Inland Revenue Service
* **VAT** - Value Added Tax
* **PAYE** - Pay-As-You-Earn
* **DST** - Digital Service Tax
* **CGT** - Capital Gains Tax

---

## **17. Contact & Support**

**Project Lead:** Salaudeen Mubarak  
**Repository:** https://github.com/Mozzicato/AI-TAX-REFORM  

**Key Stakeholders:**
* Tax Reform Challenge 2025 organizers
* Nigerian university student associations
* NYSC representatives
* FIRS communication team

---

**Document Version:** 2.0 (Graph RAG Architecture)  
**Last Updated:** November 27, 2025  
**Status:** Ready for Development & Competition Submission
