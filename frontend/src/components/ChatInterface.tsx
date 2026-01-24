'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { Send, Loader2, CheckCircle2, AlertCircle, Sparkles, Bot, User, RefreshCw, Copy, Check, ChevronDown, ChevronUp } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/utils'

interface Source {
  text: string
  page: number
  score: number
  source?: string
  chunk_id?: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  model?: string
  verified?: boolean
  isLoading?: boolean
  error?: boolean
  timestamp?: Date
}

const SUGGESTED_QUESTIONS = [
  "What is the personal income tax rate in Nigeria?",
  "How is capital gains tax calculated?",
  "What are the VAT exemptions in Nigeria?",
  "Explain the Consolidated Relief Allowance",
  "What is the minimum tax rate?",
]

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: "👋 Hello! I'm your **AI Tax Assistant** powered by the Nigeria Tax Act 2025.\n\nI can help you with:\n- 📊 Understanding tax rates and brackets\n- 💰 Tax reliefs and exemptions\n- 📋 Compliance requirements\n- ❓ Any questions about Nigerian tax law\n\nHow can I assist you today?",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [useVerification, setUseVerification] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set())
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  const handleCopy = useCallback(async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }, [])

  const toggleSources = useCallback((id: string) => {
    setExpandedSources(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmedInput = input.trim()
    if (!trimmedInput || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: trimmedInput,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      isLoading: true,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, loadingMessage])

    try {
      const endpoint = useVerification ? '/api/aqa' : '/api/qa'
      
      // Create abort controller for timeout
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 45000) // 45 second timeout
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: trimmedInput,
          top_k: 3, // Reduced from 5 for faster response
          prefer_grok: true,
        }),
        signal: controller.signal,
      })

      clearTimeout(timeoutId)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || data.message || `API error: ${response.status}`)
      }

      const assistantMessage: Message = {
        id: loadingMessage.id,
        role: 'assistant',
        content: data.answer || "I couldn't generate a response. Please try again.",
        sources: data.sources,
        model: data.model,
        verified: data.verified,
        timestamp: new Date(),
      }

      setMessages(prev =>
        prev.map(msg => (msg.id === loadingMessage.id ? assistantMessage : msg))
      )
    } catch (error) {
      console.error('Error:', error)
      
      let errorContent = '❌ Sorry, I encountered an error. Please try again.'
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorContent = '⏱️ **Request timed out**\n\nThe AI is taking longer than usual to respond. This might be due to high server load. Please try:\n\n- Asking a simpler question\n- Using the Tax Calculator for calculations\n- Trying again in a moment'
        } else {
          errorContent = `❌ ${error.message}`
        }
      }
      
      const errorMessage: Message = {
        id: loadingMessage.id,
        role: 'assistant',
        content: errorContent,
        error: true,
        timestamp: new Date(),
      }
      setMessages(prev =>
        prev.map(msg => (msg.id === loadingMessage.id ? errorMessage : msg))
      )
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleSuggestedQuestion = useCallback((question: string) => {
    setInput(question)
    inputRef.current?.focus()
  }, [])

  const handleRetry = useCallback((originalQuestion: string) => {
    setInput(originalQuestion)
    // Remove the last error message
    setMessages(prev => prev.slice(0, -2))
    inputRef.current?.focus()
  }, [])

  const clearChat = useCallback(() => {
    setMessages([{
      id: Date.now().toString(),
      role: 'assistant',
      content: "Chat cleared! How can I help you with Nigerian tax law?",
      timestamp: new Date(),
    }])
  }, [])

  return (
    <div className="flex flex-col h-[700px]">
      {/* Header Actions */}
      <div className="flex items-center justify-between px-4 py-2 border-b bg-gray-50/50">
        <span className="text-xs text-gray-500">
          {messages.length - 1} message{messages.length !== 2 ? 's' : ''}
        </span>
        <button
          onClick={clearChat}
          className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1 transition-colors"
        >
          <RefreshCw className="w-3 h-3" />
          Clear chat
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={cn(
              'flex gap-3',
              message.role === 'user' ? 'justify-end' : 'justify-start'
            )}
          >
            {message.role === 'assistant' && (
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center flex-shrink-0 shadow-lg">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
            
            <div
              className={cn(
                'max-w-[85%] rounded-2xl px-4 py-3 shadow-sm',
                message.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : message.error
                  ? 'bg-red-50 text-red-900 border border-red-200'
                  : 'bg-white text-gray-900 border border-gray-100'
              )}
            >
              {message.isLoading ? (
                <div className="flex items-center gap-3 py-2">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  <span className="text-sm text-gray-500">
                    {useVerification ? 'Analyzing and verifying...' : 'Thinking...'}
                  </span>
                </div>
              ) : (
                <>
                  <div className={cn(
                    "prose prose-sm max-w-none",
                    message.role === 'user' && "prose-invert"
                  )}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                  
                  {/* Message metadata and actions */}
                  {message.role === 'assistant' && !message.error && (
                    <div className="mt-3 pt-3 border-t border-gray-100 flex flex-wrap items-center gap-3">
                      {message.model && (
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                          {message.model}
                        </span>
                      )}
                      
                      {message.verified !== undefined && (
                        <span
                          className={cn(
                            'flex items-center gap-1 text-xs px-2 py-1 rounded-full',
                            message.verified 
                              ? 'bg-green-100 text-green-700' 
                              : 'bg-yellow-100 text-yellow-700'
                          )}
                        >
                          {message.verified ? (
                            <>
                              <CheckCircle2 className="w-3 h-3" />
                              Verified
                            </>
                          ) : (
                            <>
                              <AlertCircle className="w-3 h-3" />
                              Unverified
                            </>
                          )}
                        </span>
                      )}
                      
                      <button
                        onClick={() => handleCopy(message.content, message.id)}
                        className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1 transition-colors"
                      >
                        {copiedId === message.id ? (
                          <>
                            <Check className="w-3 h-3" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            Copy
                          </>
                        )}
                      </button>
                    </div>
                  )}

                  {/* Error retry button */}
                  {message.error && index > 0 && messages[index - 1]?.role === 'user' && (
                    <button
                      onClick={() => handleRetry(messages[index - 1].content)}
                      className="mt-3 text-xs text-red-600 hover:text-red-800 flex items-center gap-1"
                    >
                      <RefreshCw className="w-3 h-3" />
                      Retry
                    </button>
                  )}

                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <button
                        onClick={() => toggleSources(message.id)}
                        className="flex items-center gap-2 text-xs text-gray-500 hover:text-gray-700 font-medium transition-colors"
                      >
                        {expandedSources.has(message.id) ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                        {message.sources.length} source{message.sources.length !== 1 ? 's' : ''} referenced
                      </button>
                      
                      {expandedSources.has(message.id) && (
                        <div className="mt-3 space-y-2">
                          {message.sources.map((source, idx) => (
                            <div
                              key={idx}
                              className="p-3 bg-gray-50 rounded-lg text-xs"
                            >
                              <div className="flex justify-between items-start mb-2">
                                <span className="font-semibold text-gray-700">
                                  📄 Page {source.page}
                                </span>
                                <span className="text-gray-400 bg-gray-200 px-2 py-0.5 rounded-full">
                                  {(source.score * 100).toFixed(0)}% match
                                </span>
                              </div>
                              <p className="text-gray-600 line-clamp-4 leading-relaxed">
                                {source.text}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
            
            {message.role === 'user' && (
              <div className="w-9 h-9 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5 text-gray-600" />
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions */}
      {messages.length === 1 && (
        <div className="px-4 pb-2">
          <p className="text-xs text-gray-500 mb-2">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_QUESTIONS.map((question, idx) => (
              <button
                key={idx}
                onClick={() => handleSuggestedQuestion(question)}
                className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-full transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t p-4 bg-gray-50/80 backdrop-blur">
        <div className="mb-3 flex items-center justify-between">
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={useVerification}
              onChange={(e) => setUseVerification(e.target.checked)}
              className="w-4 h-4 rounded text-primary-600 focus:ring-primary-500 focus:ring-offset-0"
            />
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-4 h-4" />
              Enable answer verification
            </span>
            <span className="text-xs text-gray-400">(more accurate)</span>
          </label>
        </div>
        
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about tax laws, rates, exemptions, compliance..."
            className="flex-1 px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white"
            disabled={isLoading}
            maxLength={500}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className={cn(
              "px-5 py-3 rounded-xl font-medium transition-all flex items-center gap-2",
              isLoading || !input.trim()
                ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                : "bg-primary-600 text-white hover:bg-primary-700 shadow-lg shadow-primary-600/25"
            )}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
        
        <p className="text-xs text-gray-400 mt-2 text-center">
          AI responses are based on the Nigeria Tax Act 2025. Always verify with official sources.
        </p>
      </div>
    </div>
  )
}
