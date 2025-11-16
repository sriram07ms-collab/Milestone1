import React from 'react'
import Chatbot from './components/Chatbot'
import Header from './components/Header'
import FactOnlyBanner from './components/FactOnlyBanner'
import ErrorBoundary from './components/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header />
        <FactOnlyBanner />
        <main className="flex-1 container mx-auto px-4 py-8 max-w-6xl">
          <Chatbot />
        </main>
        <footer className="bg-white border-t border-gray-200 py-6 mt-auto">
          <div className="container mx-auto px-4 text-center text-sm text-gray-600">
            <p>© 2025 ICICI Prudential Mutual Fund FAQ Assistant</p>
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  )
}

export default App

