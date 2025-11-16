import React from 'react'
import { ArrowRight } from 'lucide-react'

const suggestedQuestions = [
  "What is the expense ratio of ICICI Prudential Large Cap Fund?",
  "What is the minimum SIP amount for mid cap funds?",
  "Tell me about exit load for ICICI Prudential Midcap Fund",
  "How to download mutual fund statements?",
  "What is the lock-in period for ELSS funds?",
]

function SuggestedQuestions({ onSelect }) {
  return (
    <div className="px-6 py-4 bg-white border-t border-gray-200">
      <p className="text-sm font-medium text-gray-700 mb-3">Suggested Questions:</p>
      <div className="flex flex-wrap gap-2">
        {suggestedQuestions.map((question, index) => (
          <button
            key={index}
            onClick={() => onSelect(question)}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-groww-green-50 hover:border-groww-green-300 text-gray-700 hover:text-groww-green-700 rounded-lg border border-gray-200 transition-all duration-200 text-sm font-medium group"
          >
            <span>{question}</span>
            <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
          </button>
        ))}
      </div>
    </div>
  )
}

export default SuggestedQuestions


