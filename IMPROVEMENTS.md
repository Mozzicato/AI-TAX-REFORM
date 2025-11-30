# NTRIA Improvements

## 1. Conversation Memory (Implemented)
The system now supports multi-turn conversations.

### How it works:
1. **Frontend**: `ChatWindow.jsx` collects the last 6 messages and sends them to the backend.
2. **Backend**: `rag_pipeline.py` uses Gemini to **rewrite the query** based on history.
   - Example: "Who pays it?" -> "Who is responsible for paying Value Added Tax (VAT)?"
3. **Retrieval**: The rewritten query is used to search Pinecone and the Knowledge Graph.
4. **Generation**: The original history + retrieved context is used to generate the final answer.

### Verification:
- Tested with: `User: What is VAT?` -> `User: Who pays it?`
- Result: Query rewritten successfully and context retrieved.

## 2. Read-Only Graph (Implemented)
To prevent concurrency issues and ensure stability during runtime.

### How it works:
- `JsonGraphService` now accepts a `read_only` flag (default: `True`).
- When `read_only=True`, all write operations (`add_node`, `_save`) are disabled.
- Import scripts can still write by explicitly setting `read_only=False`.

### Verification:
- Server logs show: `✅ JSON Graph initialized (READ-ONLY): 25 nodes, 1000 edges`
- Attempting to save would log a warning and do nothing.

---

## Next Steps (Recommended)
1. **UI Improvements**: Add "Starter Chips" to help users know what to ask.
2. **Streaming**: Implement streaming responses for better UX.
3. **Evaluation**: Create a golden dataset to verify accuracy.
