import React, { useState, useRef, useEffect } from 'react'
import { Send, Loader2, ExternalLink, MessageSquare } from 'lucide-react'
import { sendMessage } from '../services/api'
import MessageList from './MessageList'
import SuggestedQuestions from './SuggestedQuestions'

function Chatbot() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your factual information assistant for ICICI Prudential Mutual Funds. I can help you with information about expense ratios, exit loads, minimum SIP amounts, lock-in periods, benchmarks, and more. What would you like to know?',
      sourceUrl: null
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await sendMessage(userMessage)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.answer,
        sourceUrl: response.source_url,
        schemeName: response.scheme_name,
        factType: response.fact_type
      }])
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or check if the backend server is running.',
        sourceUrl: null
      }])
      console.error('Error sending message:', error)
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleSuggestedQuestion = (question) => {
    setInput(question)
    inputRef.current?.focus()
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden flex flex-col h-[calc(100vh-280px)] max-h-[800px]">
      {/* Chat Header */}
      <div className="bg-gradient-to-r from-groww-green-500 to-groww-green-600 px-6 py-4">
        <div className="flex items-center space-x-3">
          <div className="bg-white/20 p-2 rounded-lg">
            <MessageSquare className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-white font-semibold text-lg">Chat Assistant</h2>
            <p className="text-white/90 text-sm">Ask questions about ICICI Prudential Mutual Funds</p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
        <MessageList messages={messages} />
        {isLoading && (
          <div className="flex justify-start">
            <div className="chat-message assistant">
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions (shown when no messages except initial) */}
      {messages.length === 1 && (
        <SuggestedQuestions onSelect={handleSuggestedQuestion} />
      )}

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white p-4">
        <form onSubmit={handleSend} className="flex items-end space-x-3">
          <div className="flex-1">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about expense ratio, exit load, minimum SIP, lock-in period..."
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-groww-green-500 focus:border-transparent"
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="bg-groww-green-500 hover:bg-groww-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-colors duration-200 flex items-center justify-center min-w-[48px]"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Chatbot

