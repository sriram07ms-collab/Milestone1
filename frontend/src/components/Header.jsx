import React from 'react'
import { MessageCircle } from 'lucide-react'

function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-groww-green-500 p-2 rounded-lg">
              <MessageCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                ICICI Prudential Mutual Fund FAQ
              </h1>
              <p className="text-sm text-gray-600">Factual Information Assistant</p>
            </div>
          </div>
          <div className="hidden md:flex items-center space-x-2 text-sm">
            <span className="px-3 py-1 bg-groww-green-100 text-groww-green-700 rounded-full font-medium">
              Fact Only
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header


