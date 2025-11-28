# NTRIA API Documentation

Complete API reference for the Nigeria Tax Reform Intelligence Assistant backend.

## Base URL

```
http://localhost:8000 (local development)
https://api.ntria.com (production - to be deployed)
```

## API Versioning

All endpoints are versioned with `/api/v1/` prefix.

---

## Table of Contents

1. [Chat Endpoints](#chat-endpoints)
2. [Knowledge Graph Endpoints](#knowledge-graph-endpoints)
3. [Analytics Endpoints](#analytics-endpoints)
4. [Status Endpoints](#status-endpoints)
5. [Authentication](#authentication)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)

---

## Chat Endpoints

### POST /api/v1/chat

Send a user query and receive an answer with sources and confidence score.

#### Request

```json
{
  "message": "What are the VAT registration requirements?",
  "session_id": "user-session-123",
  "conversation_history": [
    {
      "role": "user",
      "content": "What is VAT?"
    },
    {
      "role": "assistant",
      "content": "VAT is Value Added Tax..."
    }
  ],
  "context": {
    "taxpayer_type": "business",
    "state": "Lagos"
  }
}
```

#### Request Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | ✅ | User query (2-5000 characters) |
| `session_id` | string | ❌ | User session identifier |
| `conversation_history` | array | ❌ | Previous messages in conversation |
| `context` | object | ❌ | Additional context (taxpayer type, location, etc.) |

#### Response

```json
{
  "answer": "VAT registration is required if your annual turnover exceeds ₦25 million...",
  "sources": [
    {
      "title": "Nigeria-Tax-Act-2025",
      "page": 42,
      "section": "VAT Registration",
      "type": "document"
    }
  ],
  "confidence": 0.92,
  "session_id": "user-session-123",
  "retrieval_stats": {
    "graph_results": 5,
    "vector_results": 3,
    "fused_results": 8
  },
  "valid": true
}
```

#### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Generated response to user query |
| `sources` | array | List of sources used to generate answer |
| `confidence` | number | Confidence score (0.0 - 1.0) |
| `session_id` | string | Session identifier |
| `retrieval_stats` | object | Retrieval performance statistics |
| `valid` | boolean | Whether response passed validation |

#### Status Codes

| Code | Description |
|------|-------------|
| 200 | Successful response |
| 400 | Invalid request (missing message, empty message) |
| 422 | Validation error (invalid data types) |
| 500 | Server error (API key missing, service unavailable) |

#### Example

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the penalties for late VAT filing?",
    "session_id": "user-456"
  }'
```

---

## Knowledge Graph Endpoints

### GET /api/v1/entities

Retrieve available tax entities from the knowledge graph.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `entity_type` | string | Optional: Filter by entity type (Tax, Taxpayer, Agency, Process, etc.) |

#### Response

```json
{
  "Tax": ["VAT", "PAYE", "DST", "Capital Gains Tax"],
  "Taxpayer": ["Individual", "Freelancer", "SME", "Digital Service Provider"],
  "Agency": ["FIRS", "JTB", "State IRS"],
  "Process": ["VAT Registration", "PAYE Filing", "Annual Return"],
  "Penalty": ["Interest Charge", "Late Filing Charge", "Fraud Penalty"]
}
```

#### Example

```bash
# Get all entities
curl http://localhost:8000/api/v1/entities

# Get only Tax entities
curl http://localhost:8000/api/v1/entities?entity_type=Tax
```

---

### POST /api/v1/graph/search

Execute a custom Cypher query on the Neo4j knowledge graph.

#### Request

```json
{
  "cypher": "MATCH (tax:Tax)-[:applies_to]->(taxpayer:Taxpayer) WHERE tax.name = 'VAT' RETURN taxpayer.name"
}
```

#### Response

```json
{
  "results": {
    "matches": [
      {
        "taxpayer": {
          "name": "Business",
          "id": "taxpayer_001"
        }
      }
    ],
    "execution_time": 125
  }
}
```

#### Example

```bash
curl -X POST http://localhost:8000/api/v1/graph/search \
  -H "Content-Type: application/json" \
  -d '{
    "cypher": "MATCH (n:Tax) RETURN n LIMIT 5"
  }'
```

---

## Analytics Endpoints

### GET /api/v1/analytics

Get analytics and usage statistics.

#### Query Parameters

| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `time_period` | string | `day` | `hour`, `day`, `week`, `month` |

#### Response

```json
{
  "time_period": "day",
  "total_queries": 1250,
  "average_confidence": 0.87,
  "top_questions": [
    {
      "question": "What is VAT?",
      "count": 156,
      "avg_confidence": 0.91
    },
    {
      "question": "How do I register for taxes?",
      "count": 143,
      "avg_confidence": 0.85
    }
  ],
  "entity_frequency": {
    "VAT": 234,
    "PAYE": 189,
    "DST": 145
  },
  "performance_metrics": {
    "avg_response_time": 2.3,
    "p95_response_time": 4.5,
    "error_rate": 0.02
  }
}
```

#### Example

```bash
# Get daily analytics
curl http://localhost:8000/api/v1/analytics

# Get weekly analytics
curl http://localhost:8000/api/v1/analytics?time_period=week
```

---

## Status Endpoints

### GET /health

Simple health check for load balancers and monitoring.

#### Response

```json
{
  "status": "healthy",
  "service": "NTRIA API",
  "version": "1.0.0"
}
```

#### Status Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200 | healthy | Service is operational |
| 503 | unhealthy | Service is down or degraded |

---

### GET /api/v1/status

Get detailed status of all components.

#### Response

```json
{
  "api": "healthy",
  "components": {
    "neo4j": "healthy",
    "vector_db": "healthy",
    "openai": "healthy"
  },
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

### GET /api/v1/info

Get API metadata and available endpoints.

#### Response

```json
{
  "name": "NTRIA API",
  "description": "Nigeria Tax Reform Intelligence Assistant - Graph RAG Backend",
  "version": "1.0.0",
  "endpoints": {
    "chat": "/api/v1/chat",
    "entities": "/api/v1/entities",
    "graph_search": "/api/v1/graph/search",
    "analytics": "/api/v1/analytics",
    "status": "/api/v1/status",
    "docs": "/api/docs",
    "redoc": "/api/redoc"
  },
  "models": {
    "language_model": "gpt-4",
    "embedding_model": "text-embedding-3-small"
  }
}
```

---

## Authentication

### Current Status: No Authentication

The API currently operates without authentication for development. In production, implement:

```
Authorization: Bearer <api-key>
```

### Future Implementation

Add API key validation:

```python
@app.middleware("http")
async def validate_api_key(request: Request, call_next):
    api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not validate_api_key(api_key):
        return JSONResponse(status_code=401, content={"detail": "Invalid API key"})
    return await call_next(request)
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

#### 400 - Bad Request

```json
{
  "detail": "Message must be at least 2 characters"
}
```

#### 422 - Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 - Internal Server Error

```json
{
  "detail": "Error processing message: Connection to Neo4j failed"
}
```

### Handling Errors in Client

```typescript
try {
  const response = await apiClient.chat("What is VAT?");
} catch (error) {
  const apiError = error as ApiError;
  console.error(`Error: ${apiError.status} - ${apiError.message}`);
  
  if (apiError.status === 500) {
    // Server error - show generic message
  } else if (apiError.status === 400) {
    // Bad request - show validation error
  }
}
```

---

## Rate Limiting

### Current Status: No Rate Limiting

In production, implement rate limiting:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1234567890
```

### Suggested Limits

- **Chat endpoint**: 100 requests per minute per session
- **Graph search**: 50 requests per minute per IP
- **Analytics**: 10 requests per minute

---

## Examples

### Example 1: Simple Question

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is VAT?"
  }'
```

### Example 2: Multi-turn Conversation

```bash
# First question
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is VAT?",
    "session_id": "user-123"
  }'

# Follow-up question with history
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the registration thresholds?",
    "session_id": "user-123",
    "conversation_history": [
      {
        "role": "user",
        "content": "What is VAT?"
      },
      {
        "role": "assistant",
        "content": "VAT is Value Added Tax..."
      }
    ]
  }'
```

### Example 3: Context-Aware Query

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my tax obligations?",
    "context": {
      "taxpayer_type": "SME",
      "annual_turnover": 50000000,
      "state": "Lagos",
      "industry": "Retail Trade"
    }
  }'
```

### Example 4: Graph Query

```bash
curl -X POST http://localhost:8000/api/v1/graph/search \
  -H "Content-Type: application/json" \
  -d '{
    "cypher": "MATCH (tax:Tax)-[:applies_to]->(taxpayer:Taxpayer) RETURN tax.name, taxpayer.name LIMIT 10"
  }'
```

### Example 5: Using Python Client

```python
from app.services.apiClient import apiClient

# Send message
response = await apiClient.chat(
    message="What are VAT penalties?",
    session_id="user-789"
)

print(f"Answer: {response.answer}")
print(f"Confidence: {response.confidence}")
print(f"Sources: {[s.title for s in response.sources]}")
```

### Example 6: Using TypeScript Client

```typescript
import { apiClient } from '@/services/apiClient';

// Send message
try {
  const response = await apiClient.chat(
    "How do I file my annual return?",
    undefined,
    { taxpayer_type: "Individual" }
  );
  
  console.log("Answer:", response.answer);
  console.log("Confidence:", response.confidence);
  console.log("Sources:", response.sources);
} catch (error) {
  console.error("API Error:", error);
}
```

---

## API Testing Tools

### Swagger UI
- **URL:** http://localhost:8000/api/docs
- **Features:** Interactive API explorer, try-it-out
- **Best for:** Learning and testing

### ReDoc
- **URL:** http://localhost:8000/api/redoc
- **Features:** Beautiful documentation
- **Best for:** Reading and understanding

### Postman
```json
{
  "name": "NTRIA API",
  "baseUrl": "http://localhost:8000",
  "requests": [
    {
      "name": "Chat",
      "method": "POST",
      "url": "/api/v1/chat",
      "body": {
        "message": "What is VAT?"
      }
    }
  ]
}
```

### cURL
```bash
# Create .bashrc function for easy testing
ntria_chat() {
  curl -X POST http://localhost:8000/api/v1/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$1\"}"
}

# Usage:
ntria_chat "What is VAT?"
```

---

## Performance Metrics

### Target Performance

| Metric | Target | Actual |
|--------|--------|--------|
| Response Time (p50) | < 2s | - |
| Response Time (p95) | < 5s | - |
| Response Time (p99) | < 10s | - |
| Availability | > 99.5% | - |
| Error Rate | < 1% | - |

### Optimization Tips

1. **Reuse session_id** for multi-turn conversations
2. **Cache frequent queries** using conversation history
3. **Use appropriate entity_type filter** for targeted searches
4. **Implement request batching** when possible

---

## Changelog

### Version 1.0.0 (Current)
- ✅ Chat endpoint with Graph RAG pipeline
- ✅ Entity retrieval
- ✅ Graph search with Cypher queries
- ✅ Analytics endpoint
- ✅ Status and health checks

### Planned Features
- 🔄 WebSocket support for streaming responses
- 🔄 File upload for document processing
- 🔄 User authentication and API keys
- 🔄 Rate limiting and quotas
- 🔄 Advanced analytics dashboard
- 🔄 Multi-language support

---

**For more information, see QUICKSTART.md and DESIGNDOC.md**
