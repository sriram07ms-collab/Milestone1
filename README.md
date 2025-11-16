# RAG-Based FAQ Chatbot for ICICI Prudential Mutual Funds

A sophisticated FAQ assistant that answers factual questions about mutual fund schemes using Retrieval-Augmented Generation (RAG) with semantic search.

## 🎯 Features

- **RAG-Based System**: Uses embeddings and vector search for semantic retrieval
- **Factual Answers Only**: No investment advice, only factual information
- **Source Attribution**: Every answer includes a source URL from Groww
- **Comprehensive Data**: Covers expense ratio, exit load, minimum SIP, lock-in periods, riskometer, benchmark, and statement downloads
- **Fast Semantic Search**: Vector database for quick and relevant retrieval

## 🏗️ Architecture

```
User Query
    ↓
Query Embedding (Sentence Transformers)
    ↓
Vector Search (ChromaDB)
    ↓
Retrieve Top-K Relevant Documents
    ↓
Augment LLM Prompt with Context
    ↓
Generate Response (Gemini AI)
    ↓
Return Answer + Source URL
```

## 📋 Prerequisites

- Python 3.8+
- Gemini API Key (get from https://makersuite.google.com/app/apikey)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
DATABASE_URL=sqlite:///./icici_funds.db
LOG_LEVEL=INFO
```

### 3. Generate Embeddings

First, ensure you have data in the database (run scrapers if needed), then generate embeddings:

```bash
python scripts/generate_embeddings.py
```

This will:
- Load all facts from the SQL database
- Generate embeddings using Sentence Transformers
- Store them in ChromaDB vector database

### 4. Start the Server

```bash
python run_server.py
```

The server will start at `http://localhost:8000`

### 5. Test the System

```bash
# Test components
python quick_test.py

# Test RAG retrieval
python test_rag_retrieval.py

# Test full API (after server starts)
python test_rag_system.py
```

## 📡 API Endpoints

### Health Check
```bash
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "rag_configured": true,
  "database_connected": true
}
```

### Chat Endpoint
```bash
POST /api/chat
Content-Type: application/json

{
  "query": "What is the expense ratio of ICICI Prudential Large Cap Fund?"
}
```

Response:
```json
{
  "answer": "The expense ratio of ICICI Prudential Large Cap Fund Direct Growth is 0.85%.",
  "source_url": "https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth",
  "scheme_name": "ICICI Prudential Large Cap Fund Direct Growth",
  "fact_type": "expense_ratio",
  "query_type": "factual_query"
}
```

### List Schemes
```bash
GET /api/schemes
```

## 🧪 Testing

### Component Tests
```bash
python quick_test.py
```

Tests:
- Embedding Service
- Vector Store
- RAG Retriever
- Database Connection
- LLM Client

### RAG Retrieval Test
```bash
python test_rag_retrieval.py
```

Tests semantic search with sample queries.

## 📊 Data Collection

### Scrape Funds
```bash
# Scrape specific funds
python scrape_specific_funds.py

# Or use the orchestrator
python -m data_collection.scraper_orchestrator
```

### Verify Database
```bash
python verify_database.py
```

## 🔧 Project Structure

```
Milestone1/
├── api/                    # FastAPI backend
│   ├── main.py            # App entry point
│   ├── routes.py          # API endpoints
│   ├── schemas.py         # Pydantic models
│   └── dependencies.py    # Dependency injection
├── chatbot/               # Chatbot logic
│   ├── llm_client.py      # Gemini AI client
│   ├── query_processor.py # Query processing with RAG
│   ├── scheme_matcher.py  # Fuzzy scheme matching
│   └── response_generator.py # Response generation
├── rag/                   # RAG system
│   ├── embedding_service.py # Embedding generation
│   ├── vector_store.py    # ChromaDB interface
│   └── rag_retriever.py   # RAG retrieval logic
├── data_collection/       # Web scraping
│   ├── groww_amc_scraper.py
│   ├── groww_fund_scraper.py
│   └── scraper_orchestrator.py
├── database/              # Database models
│   └── models.py
├── config/                # Configuration
│   └── settings.py
├── scripts/               # Utility scripts
│   └── generate_embeddings.py
└── vector_db/            # ChromaDB storage (auto-created)
```

## 🎯 Key Components

### RAG System
- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Vector Database**: ChromaDB
- **Retrieval**: Top-K semantic search with relevance scoring

### LLM
- **Model**: Gemini 2.0 Flash (Experimental)
- **Purpose**: Query understanding and response generation

### Data Storage
- **SQL Database**: SQLite (schemes and facts)
- **Vector Database**: ChromaDB (embeddings)

## 📝 Data Points Collected

For each mutual fund scheme:
- Fund Name
- Category (Equity, Debt, Hybrid, etc.)
- Risk Level
- NAV
- Expense Ratio
- 1Y/3Y/5Y Returns
- Rating
- Fund Size (in Cr)
- Exit Load
- Minimum Lump Sum Investment
- Minimum SIP Amount
- Lock-in Period (for ELSS)
- Riskometer details
- Benchmark information
- Statement Download Instructions

## 🔍 How RAG Works

1. **Query Processing**: User query is converted to an embedding
2. **Semantic Search**: Vector database finds similar documents
3. **Context Retrieval**: Top-K most relevant facts are retrieved
4. **Prompt Augmentation**: Retrieved context is added to LLM prompt
5. **Response Generation**: LLM generates answer using the context
6. **Source Attribution**: Source URL from most relevant document is included

## ⚙️ Configuration

All configuration is in `config/settings.py` and can be overridden via environment variables:

- `GEMINI_API_KEY`: Your Gemini API key
- `GEMINI_MODEL`: Model name (default: gemini-2.0-flash-exp)
- `DATABASE_URL`: SQL database connection string
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

## 🐛 Troubleshooting

### RAG Not Working
- Ensure embeddings are generated: `python scripts/generate_embeddings.py`
- Check vector database exists in `vector_db/` directory
- Verify health endpoint shows `rag_configured: true`

### LLM Errors
- Verify `GEMINI_API_KEY` is set in `.env`
- Check API key is valid and has quota
- Ensure `google-generativeai` package is installed

### Database Issues
- Check database file exists: `icici_funds.db`
- Verify data is populated: `python verify_database.py`
- Check database permissions

## 📈 Performance

- **Embedding Generation**: ~0.6s for 30 documents
- **Vector Search**: <100ms per query
- **Total Response Time**: ~1-3 seconds (including LLM)

## 🎉 Status

✅ **System Complete and Tested**

All components are working:
- ✅ Data collection
- ✅ Database storage
- ✅ Embedding generation
- ✅ Vector database
- ✅ RAG retrieval
- ✅ Backend API
- ✅ LLM integration

## 📄 License

This project is for educational/demonstration purposes.

## 🙏 Acknowledgments

- Uses [Sentence Transformers](https://www.sbert.net/) for embeddings
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage
- Uses [Gemini AI](https://deepmind.google/technologies/gemini/) for LLM
- Data sourced from [Groww](https://groww.in/)
