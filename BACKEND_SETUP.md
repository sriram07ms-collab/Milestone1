# Backend Setup Guide

## Overview

The backend is built using FastAPI with Gemini AI (gemini-2.0-flash-exp) for the FAQ chatbot.

## Architecture

```
┌─────────────┐
│   FastAPI   │  (API Layer)
│   Server     │
└──────┬──────┘
       │
       ├───> Query Processor (LLM-based intent extraction)
       ├───> Scheme Matcher (Fuzzy matching)
       ├───> Response Generator (LLM-based response)
       └───> Database (SQLite/PostgreSQL)
```

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
Create a `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
DATABASE_URL=sqlite:///./icici_funds.db
LOG_LEVEL=INFO
```

3. **Get Gemini API Key:**
   - Visit https://makersuite.google.com/app/apikey
   - Create a new API key
   - Add it to your `.env` file

## Running the Server

```bash
python run_server.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### 1. POST `/api/chat`
Main chat endpoint for FAQ queries.

**Request:**
```json
{
  "query": "What is the expense ratio of ICICI Prudential Large Cap Fund?",
  "conversation_id": "optional"
}
```

**Response:**
```json
{
  "answer": "The expense ratio of ICICI Prudential Large Cap Fund is 0.85%...",
  "source_url": "https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth",
  "scheme_name": "ICICI Prudential Large Cap Fund Direct Growth",
  "fact_type": "expense_ratio",
  "query_type": "specific_fund",
  "last_updated": "2025-11-15"
}
```

### 2. GET `/api/schemes`
Get list of all schemes.

**Response:**
```json
{
  "schemes": [...],
  "total": 5
}
```

### 3. GET `/api/schemes/{scheme_id}`
Get detailed information about a specific scheme.

### 4. GET `/api/health`
Health check endpoint.

## Testing

Run the test script:
```bash
python test_backend.py
```

Make sure the server is running first!

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Components

### 1. LLM Client (`chatbot/llm_client.py`)
- Handles Gemini AI integration
- Model: gemini-2.0-flash-exp
- Supports structured and unstructured responses

### 2. Query Processor (`chatbot/query_processor.py`)
- Extracts intent from user queries
- Identifies scheme names
- Determines query type (specific_fund, category_query, general)

### 3. Scheme Matcher (`chatbot/scheme_matcher.py`)
- Fuzzy matching for scheme names
- Handles variations in naming
- Category-based filtering

### 4. Response Generator (`chatbot/response_generator.py`)
- Generates responses using LLM
- Formats data from database
- Includes source URLs

### 5. API Routes (`api/routes.py`)
- RESTful API endpoints
- Error handling
- Request/response validation

## Error Handling

The backend includes comprehensive error handling:
- Database connection errors
- LLM API errors
- Invalid requests
- Missing data

All errors are logged and return appropriate HTTP status codes.

## Next Steps

1. Set up Gemini API key
2. Run the server
3. Test the endpoints
4. Integrate with frontend (if needed)

