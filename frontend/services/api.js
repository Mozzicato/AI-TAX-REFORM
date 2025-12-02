import axios from "axios";

// Use Railway backend URL (configured via environment variable)
const API_ROOT_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
// API endpoints are under /api/v1
const API_BASE_URL = `${API_ROOT_URL}/api/v1`;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ============================================================================
// CHAT ENDPOINTS
// ============================================================================

/**
 * Send a message to the tax bot
 * @param {string} message - User question
 * @param {string} sessionId - Session identifier
 * @param {object} context - Optional context (taxpayer type, income, etc.)
 * @param {Array} history - Conversation history
 * @returns {Promise} Response from backend
 */
export const sendMessage = async (message, sessionId, context = {}, history = []) => {
  try {
    const response = await api.post("/chat", {
      message,
      session_id: sessionId,
      context,
      conversation_history: history,
    });
    return response.data;
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
};

// ============================================================================
// ENTITY ENDPOINTS
// ============================================================================

/**
 * Get all available entities (for autocomplete)
 * @param {string} type - Entity type (Tax, Taxpayer, Agency, etc.)
 * @returns {Promise} List of entities
 */
export const getEntities = async (type = null) => {
  try {
    const params = type ? { type } : {};
    const response = await api.get("/entities", { params });
    return response.data;
  } catch (error) {
    console.error("Error fetching entities:", error);
    throw error;
  }
};

// ============================================================================
// GRAPH SEARCH ENDPOINTS
// ============================================================================

/**
 * Search the knowledge graph
 * @param {string} query - Search query
 * @param {object} filters - Optional filters
 * @returns {Promise} Search results
 */
export const graphSearch = async (query, filters = {}) => {
  try {
    const response = await api.post("/graph/search", {
      query,
      filters,
    });
    return response.data;
  } catch (error) {
    console.error("Error searching graph:", error);
    throw error;
  }
};

// ============================================================================
// HEALTH CHECK
// ============================================================================

/**
 * Check if backend is healthy
 * @returns {Promise} Health status
 */
export const checkHealth = async () => {
  try {
    // Call the Railway backend health endpoint directly
    // Health check is at the root, not under /api/v1
    const response = await axios.get(`${API_ROOT_URL}/health`, {
      timeout: 5000,
    });
    return response.data;
  } catch (error) {
    console.error("Error checking health:", error);
    throw error;
  }
};

export default api;
