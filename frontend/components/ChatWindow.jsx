import React, { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import InputField from "./InputField";
import { sendMessage } from "../services/api";

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
  const [sessionId] = useState(`session_${Date.now()}`);
  const messagesEndRef = useRef(null);

  // Starter Chips
  const starterChips = [
    "💰 VAT Rates for 2025",
    "🏢 SME Tax Exemptions",
    "📅 Filing Deadlines",
    "📝 Personal Income Tax"
  ];

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
      // Prepare history (last 6 messages)
      const history = messages.slice(-6).map(msg => ({
        role: msg.isBot ? "assistant" : "user",
        content: msg.text
      }));

      // Call the actual backend API
      const response = await sendMessage(message, sessionId, {}, history);
      
      // Simulate typing effect
      const fullText = response.answer || response.response || "I received your question but couldn't generate a response.";
      let currentText = "";
      const botMessageId = messages.length + 2;
      
      // Initial empty bot message
      setMessages((prev) => [...prev, {
        id: botMessageId,
        text: "",
        isBot: true,
        sources: response.sources || [],
        isTyping: true
      }]);
      
      setIsLoading(false);

      // Typing animation loop
      const words = fullText.split(" ");
      for (let i = 0; i < words.length; i++) {
        currentText += words[i] + " ";
        // Update message content progressively
        setMessages((prev) => prev.map(msg => 
          msg.id === botMessageId ? { ...msg, text: currentText } : msg
        ));
        // Small delay between words (adjust speed here)
        await new Promise(resolve => setTimeout(resolve, 30));
      }
      
      // Final update to ensure exact text and remove typing status
      setMessages((prev) => prev.map(msg => 
        msg.id === botMessageId ? { ...msg, text: fullText, isTyping: false } : msg
      ));

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
        {messages.length === 1 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4">
            {starterChips.map((chip, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(chip)}
                className="text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg text-sm text-gray-700 transition-colors"
              >
                {chip}
              </button>
            ))}
          </div>
        )}

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
