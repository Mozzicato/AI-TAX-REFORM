import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

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
 * @returns {Promise} Response from backend
 */
export const sendMessage = async (message, sessionId, context = {}) => {
  try {
    const response = await api.post("/chat", {
      message,
      session_id: sessionId,
      context,
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
    const response = await api.get("/health");
    return response.data;
  } catch (error) {
    console.error("Error checking health:", error);
    throw error;
  }
};

export default api;
