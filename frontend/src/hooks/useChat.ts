/**
 * React Hook for Chat API Integration
 * Manages chat state, API calls, and error handling
 */

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { apiClient, ChatResponse, Message, ApiError } from '@/services/apiClient';

interface ChatState {
  messages: Message[];
  loading: boolean;
  error: string | null;
  sessionId: string | null;
}

interface UseChatOptions {
  initialSessionId?: string;
  onError?: (error: ApiError) => void;
  onSuccess?: (response: ChatResponse) => void;
}

/**
 * Hook for managing chat functionality
 */
export function useChat(options: UseChatOptions = {}) {
  const [state, setState] = useState<ChatState>({
    messages: [],
    loading: false,
    error: null,
    sessionId: options.initialSessionId || null,
  });

  const conversationHistoryRef = useRef<Message[]>([]);

  // Set session ID on mount or when initialSessionId changes
  useEffect(() => {
    if (options.initialSessionId) {
      apiClient.setSessionId(options.initialSessionId);
      setState((prev: ChatState) => ({ ...prev, sessionId: options.initialSessionId || null }));
    }
  }, [options.initialSessionId]);

  /**
   * Send a chat message and get response
   */
  const sendMessage = useCallback(
    async (userMessage: string, context?: Record<string, any>) => {
      if (!userMessage.trim()) {
        setState((prev) => ({
          ...prev,
          error: 'Message cannot be empty',
        }));
        return;
      }

      try {
        setState((prev: ChatState) => ({
          ...prev,
          loading: true,
          error: null,
        }));

        // Add user message to history
        const newUserMessage: Message = {
          role: 'user',
          content: userMessage,
          timestamp: new Date().toISOString(),
        };

        conversationHistoryRef.current.push(newUserMessage);

        // Call API
        const response = await apiClient.chat(
          userMessage,
          conversationHistoryRef.current,
          context
        );

        // Add assistant response to history
        const assistantMessage: Message = {
          role: 'assistant',
          content: response.answer,
          timestamp: new Date().toISOString(),
          sources: response.sources,
        };

        conversationHistoryRef.current.push(assistantMessage);

        // Update state
        setState((prev: ChatState) => ({
          ...prev,
          messages: [
            ...prev.messages,
            newUserMessage,
            assistantMessage,
          ],
          loading: false,
          sessionId: response.session_id || prev.sessionId,
        }));

        // Update session ID in API client
        if (response.session_id) {
          apiClient.setSessionId(response.session_id);
        }

        // Call success callback
        if (options.onSuccess) {
          options.onSuccess(response);
        }

        return response;
      } catch (error) {
        const apiError = error as ApiError;
        setState((prev: ChatState) => ({
          ...prev,
          loading: false,
          error: apiError.message,
        }));

        if (options.onError) {
          options.onError(apiError);
        }

        throw error;
      }
    },
    [options]
  );

  /**
   * Clear chat history
   */
  const clearHistory = useCallback(() => {
    setState((prev: ChatState) => ({
      ...prev,
      messages: [],
    }));
    conversationHistoryRef.current = [];
  }, []);

  /**
   * Remove last message pair (user + assistant)
   */
  const undoLastMessage = useCallback(() => {
    setState((prev: ChatState) => {
      const newMessages = [...prev.messages];
      // Remove last message (could be user or assistant)
      if (newMessages.length > 0) {
        newMessages.pop();
        // If there's another message, remove it too (the pair)
        if (newMessages.length > 0 && newMessages[newMessages.length - 1].role === 'user') {
          newMessages.pop();
        }
      }
      return { ...prev, messages: newMessages };
    });

    // Also update conversation history ref
    if (conversationHistoryRef.current.length > 0) {
      conversationHistoryRef.current.pop();
      if (conversationHistoryRef.current.length > 0) {
        conversationHistoryRef.current.pop();
      }
    }
  }, []);

  /**
   * Set an error message
   */
  const setError = useCallback((error: string | null) => {
    setState((prev: ChatState) => ({ ...prev, error }));
  }, []);

  return {
    // State
    messages: state.messages,
    loading: state.loading,
    error: state.error,
    sessionId: state.sessionId,
    hasMessages: state.messages.length > 0,

    // Actions
    sendMessage,
    clearHistory,
    undoLastMessage,
    setError,

    // Helpers
    getConversationHistory: () => conversationHistoryRef.current,
  };
}
