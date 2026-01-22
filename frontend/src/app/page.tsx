'use client'

import { useState, useEffect } from 'react'
import ChatInterface from '@/components/ChatInterface'
import TaxCalculator from '@/components/TaxCalculator'
import { BookOpen, Calculator, MessageSquare, Shield, Zap, FileText, ExternalLink } from 'lucide-react'

type Tab = 'chat' | 'calculator'

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>('chat')
  const [isApiHealthy, setIsApiHealthy] = useState<boolean | null>(null)

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('/api/health')
        setIsApiHealthy(response.ok)
      } catch {
        setIsApiHealthy(false)
      }
    }
    checkHealth()
  }, [])

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50">
      {/* API Status Banner */}
      {isApiHealthy === false && (
        <div className="bg-amber-500 text-amber-950 text-center py-2 text-sm font-medium">
          ⚠️ Backend service is currently unavailable. Some features may not work.
        </div>
      )}

      <div className="container mx-auto px-4 py-6 max-w-7xl">
        {/* Header */}
        <header className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-3">
            <div className="p-3 bg-gradient-to-br from-primary-500 to-cyan-500 rounded-2xl shadow-lg shadow-primary-500/25">
              <BookOpen className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-gray-900 via-primary-700 to-cyan-700 bg-clip-text text-transparent">
                AI Tax Reform Assistant
              </h1>
            </div>
          </div>
          <p className="text-gray-600 text-lg max-w-2xl mx-auto">
            Your intelligent guide to Nigerian tax law powered by the <span className="font-semibold text-primary-600">Nigeria Tax Act 2025</span>
          </p>
        </header>

        {/* Feature Pills */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-8">
          <div className="flex items-center gap-2 bg-white/80 backdrop-blur px-4 py-2 rounded-full text-sm text-gray-600 shadow-sm border border-gray-100">
            <Zap className="w-4 h-4 text-amber-500" />
            <span>AI-Powered Answers</span>
          </div>
          <div className="flex items-center gap-2 bg-white/80 backdrop-blur px-4 py-2 rounded-full text-sm text-gray-600 shadow-sm border border-gray-100">
            <Shield className="w-4 h-4 text-green-500" />
            <span>Verified Responses</span>
          </div>
          <div className="flex items-center gap-2 bg-white/80 backdrop-blur px-4 py-2 rounded-full text-sm text-gray-600 shadow-sm border border-gray-100">
            <FileText className="w-4 h-4 text-blue-500" />
            <span>Source Citations</span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-t-2xl shadow-sm border border-gray-200 border-b-0">
          <div className="flex gap-1 p-2">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex-1 sm:flex-none flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
                activeTab === 'chat'
                  ? 'bg-gradient-to-r from-primary-600 to-cyan-600 text-white shadow-lg shadow-primary-600/25'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <MessageSquare className="w-5 h-5" />
              <span>Tax Q&A</span>
            </button>
            <button
              onClick={() => setActiveTab('calculator')}
              className={`flex-1 sm:flex-none flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
                activeTab === 'calculator'
                  ? 'bg-gradient-to-r from-primary-600 to-cyan-600 text-white shadow-lg shadow-primary-600/25'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Calculator className="w-5 h-5" />
              <span>Tax Calculator</span>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-b-2xl shadow-xl border border-gray-200 border-t-0">
          {activeTab === 'chat' ? <ChatInterface /> : <TaxCalculator />}
        </div>

        {/* Quick Links */}
        <div className="mt-8 grid sm:grid-cols-3 gap-4">
          <a
            href="https://firs.gov.ng"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-4 bg-white/60 backdrop-blur rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all group"
          >
            <div className="p-2 bg-primary-100 rounded-lg group-hover:bg-primary-200 transition-colors">
              <ExternalLink className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="font-semibold text-gray-900 text-sm">FIRS Portal</p>
              <p className="text-xs text-gray-500">Official tax authority</p>
            </div>
          </a>
          <a
            href="#"
            className="flex items-center gap-3 p-4 bg-white/60 backdrop-blur rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all group"
          >
            <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors">
              <FileText className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="font-semibold text-gray-900 text-sm">Tax Act 2025</p>
              <p className="text-xs text-gray-500">View full document</p>
            </div>
          </a>
          <a
            href="#"
            className="flex items-center gap-3 p-4 bg-white/60 backdrop-blur rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all group"
          >
            <div className="p-2 bg-amber-100 rounded-lg group-hover:bg-amber-200 transition-colors">
              <BookOpen className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="font-semibold text-gray-900 text-sm">User Guide</p>
              <p className="text-xs text-gray-500">How to use this tool</p>
            </div>
          </a>
        </div>

        {/* Footer */}
        <footer className="text-center mt-10 pb-6">
          <div className="flex items-center justify-center gap-2 text-sm text-gray-500 mb-2">
            <span>Powered by AI</span>
            <span>•</span>
            <span>Based on Nigeria Tax Act 2025</span>
          </div>
          <p className="text-xs text-gray-400">
            © {new Date().getFullYear()} AI Tax Reform. For informational purposes only. 
            Consult a tax professional for official advice.
          </p>
        </footer>
      </div>
    </main>
  )
}
