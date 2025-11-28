/**
 * API Client for NTRIA Backend
 * Handles all HTTP requests to the FastAPI backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// TYPES
// ============================================================================

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface Source {
  title: string;
  page?: number;
  section?: string;
  type: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  conversation_history?: Message[];
  context?: Record<string, any>;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  confidence: number;
  session_id?: string;
  retrieval_stats?: Record<string, any>;
  valid: boolean;
}

export interface Entity {
  id: string;
  name: string;
  type: string;
  description?: string;
}

export interface ApiError {
  status: number;
  message: string;
  details?: any;
}

// ============================================================================
// API CLIENT CLASS
// ============================================================================

class NTRIAApiClient {
  private client: AxiosInstance;
  private sessionId: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => this.handleError(error)
    );
  }

  /**
   * Set session ID for subsequent requests
   */
  setSessionId(sessionId: string): void {
    this.sessionId = sessionId;
  }

  /**
   * Get current session ID
   */
  getSessionId(): string | null {
    return this.sessionId;
  }

  /**
   * Main chat endpoint - send user message and get response
   */
  async chat(
    message: string,
    conversationHistory?: Message[],
    context?: Record<string, any>
  ): Promise<ChatResponse> {
    const request: ChatRequest = {
      message,
      session_id: this.sessionId || undefined,
      conversation_history: conversationHistory,
      context,
    };

    const response = await this.client.post<ChatResponse>(
      '/api/v1/chat',
      request
    );

    // Update session ID if provided
    if (response.data.session_id) {
      this.sessionId = response.data.session_id;
    }

    return response.data;
  }

  /**
   * Get available tax entities from knowledge graph
   */
  async getEntities(entityType?: string): Promise<Record<string, string[]>> {
    const params = entityType ? { entity_type: entityType } : {};

    const response = await this.client.get<Record<string, string[]>>(
      '/api/v1/entities',
      { params }
    );

    return response.data;
  }

  /**
   * Execute custom Cypher query on the knowledge graph
   */
  async graphSearch(cypher: string): Promise<Record<string, any>> {
    const response = await this.client.post<Record<string, any>>(
      '/api/v1/graph/search',
      { cypher }
    );

    return response.data;
  }

  /**
   * Get analytics and usage statistics
   */
  async getAnalytics(timePeriod: 'hour' | 'day' | 'week' | 'month' = 'day'): Promise<Record<string, any>> {
    const response = await this.client.get<Record<string, any>>(
      '/api/v1/analytics',
      { params: { time_period: timePeriod } }
    );

    return response.data;
  }

  /**
   * Get API status and component health
   */
  async getStatus(): Promise<Record<string, any>> {
    const response = await this.client.get<Record<string, any>>(
      '/api/v1/status'
    );

    return response.data;
  }

  /**
   * Get API information
   */
  async getInfo(): Promise<Record<string, any>> {
    const response = await this.client.get<Record<string, any>>(
      '/api/v1/info'
    );

    return response.data;
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<Record<string, any>> {
    const response = await this.client.get<Record<string, any>>(
      '/health'
    );

    return response.data;
  }

  /**
   * Error handler
   */
  private handleError(error: AxiosError): Promise<never> {
    const apiError: ApiError = {
      status: error.response?.status || 500,
      message: error.message,
      details: error.response?.data,
    };

    // Log error for debugging
    console.error('API Error:', apiError);

    return Promise.reject(apiError);
  }
}

// ============================================================================
// EXPORT SINGLETON
// ============================================================================

export const apiClient = new NTRIAApiClient();

export default NTRIAApiClient;
