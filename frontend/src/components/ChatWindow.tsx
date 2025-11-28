/**
 * Chat Window Component
 * Main chat interface showing conversation and message input
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import MessageBubble from '@/components/MessageBubble';
import InputField from '@/components/InputField';
import { ChatResponse } from '@/services/apiClient';

interface ChatWindowProps {
  onMessageSent?: (response: ChatResponse) => void;
  onError?: (error: string) => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  onMessageSent,
  onError,
}) => {
  const {
    messages,
    loading,
    error,
    sendMessage,
    clearHistory,
  } = useChat({
    onError: (err) => {
      if (onError) {
        onError(err.message);
      }
    },
    onSuccess: (response) => {
      if (onMessageSent) {
        onMessageSent(response);
      }
    },
  });

  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || loading) return;

    const message = inputValue;
    setInputValue('');

    try {
      await sendMessage(message);
    } catch (err) {
      console.error('Error sending message:', err);
    }
  };

  const handleClearHistory = () => {
    if (confirm('Are you sure you want to clear the chat history?')) {
      clearHistory();
      setInputValue('');
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 shadow-md">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">NTRIA</h1>
            <p className="text-blue-100 text-sm">Nigeria Tax Reform Intelligence Assistant</p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={handleClearHistory}
              className="px-3 py-2 rounded bg-blue-500 hover:bg-blue-400 text-white text-sm transition-colors"
              title="Clear conversation history"
            >
              Clear History
            </button>
          )}
        </div>
      </div>

      {/* Messages Container */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 max-w-4xl mx-auto w-full"
      >
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-6xl mb-4">📋</div>
              <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                Welcome to NTRIA
              </h2>
              <p className="text-gray-500 mb-4 max-w-md">
                Ask me any questions about Nigeria's tax reforms, regulations, processes,
                and compliance requirements.
              </p>
              <div className="text-sm text-gray-400 space-y-2">
                <p>Try asking:</p>
                <ul className="list-disc list-inside text-left inline-block">
                  <li>What are the VAT registration requirements?</li>
                  <li>How do I comply with the new DST?</li>
                  <li>What are the penalties for late filing?</li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <MessageBubble
                key={index}
                message={message.content}
                isUser={message.role === 'user'}
                timestamp={message.timestamp}
              />
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-gray-500">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                <span className="text-sm ml-2">Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-4xl mx-auto w-full px-4 py-2 bg-red-100 border border-red-400 text-red-700 rounded">
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white p-4">
        <div className="max-w-4xl mx-auto">
          <InputField
            value={inputValue}
            onChange={setInputValue}
            onSend={handleSendMessage}
            disabled={loading}
            placeholder="Ask about tax reforms, compliance, processes..."
          />
          <p className="text-xs text-gray-400 mt-2 text-center">
            NTRIA uses AI to answer questions. Always verify critical information with official sources.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
