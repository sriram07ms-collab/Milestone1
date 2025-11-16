import React from 'react'
import { Info, AlertCircle } from 'lucide-react'

function FactOnlyBanner() {
  return (
    <div className="bg-blue-50 border-b border-blue-200">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-center space-x-2 text-sm">
          <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0" />
          <p className="text-blue-800 font-medium">
            <strong>Fact Only Service:</strong> This chatbot provides factual information about mutual fund schemes only. 
            It does not provide investment advice, recommendations, or suggestions.
          </p>
        </div>
      </div>
    </div>
  )
}

export default FactOnlyBanner


