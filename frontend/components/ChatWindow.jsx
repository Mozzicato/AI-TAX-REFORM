import React, { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import InputField from "./InputField";

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi! I'm NTRIA, your Nigeria Tax Reform Intelligence Assistant. Ask me anything about the 2025 Tax Reform Act. 🇳🇬",
      isBot: true,
      sources: [],
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (message) => {
    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: message,
      isBot: false,
      sources: [],
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // TODO: Call backend API with sendMessage()
      // For now, show a placeholder response
      
      setTimeout(() => {
        const botMessage = {
          id: messages.length + 2,
          text: "Thank you for your question! The backend API integration is coming soon. This is a demo response.",
          isBot: true,
          sources: [
            { title: "Tax Reform Act 2025", section: 3 },
            { title: "FIRS Guidelines" },
          ],
        };

        setMessages((prev) => [...prev, botMessage]);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = {
        id: messages.length + 2,
        text: "Sorry, there was an error processing your question. Please try again.",
        isBot: true,
        sources: [],
      };

      setMessages((prev) => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white p-4 rounded-t-lg">
        <h1 className="text-2xl font-bold">NTRIA</h1>
        <p className="text-sm">Nigeria Tax Reform Intelligence Assistant</p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg.text}
            isBot={msg.isBot}
            sources={msg.sources}
          />
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 px-4 py-3 rounded-lg">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <InputField onSend={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}
