import React from 'react'
import { ExternalLink, CheckCircle } from 'lucide-react'

function MessageList({ messages }) {
  return (
    <>
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div className={`chat-message ${message.role}`}>
            <p className="whitespace-pre-wrap">{message.content}</p>
            
            {message.role === 'assistant' && message.sourceUrl && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <a
                  href={message.sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-2 text-sm text-groww-green-600 hover:text-groww-green-700 font-medium"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>View Source on Groww</span>
                </a>
              </div>
            )}
            
            {message.role === 'assistant' && message.schemeName && (
              <div className="mt-2 flex items-center space-x-1 text-xs text-gray-600">
                <CheckCircle className="w-3 h-3" />
                <span>Scheme: {message.schemeName}</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </>
  )
}

export default MessageList


