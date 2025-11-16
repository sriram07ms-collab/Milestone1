# RAG System Setup Guide

## Overview

The system has been converted to a **RAG (Retrieval-Augmented Generation)** based chatbot using:
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB
- **Semantic Search**: Vector similarity search

## Architecture

```
User Query
    ↓
Query Embedding (Sentence Transformers)
    ↓
Vector Search (ChromaDB)
    ↓
Retrieve Top-K Relevant Documents
    ↓
Augment LLM Prompt with Retrieved Context
    ↓
Generate Response (Gemini)
```

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `chromadb` - Vector database
- `sentence-transformers` - Embedding generation

### 2. Generate Embeddings

Before using the RAG system, you need to generate embeddings for all facts:

```bash
python scripts/generate_embeddings.py
```

This script will:
- Load all schemes and facts from the database
- Generate embeddings for each fact
- Store embeddings in ChromaDB vector database
- Create searchable documents with metadata

**Expected Output:**
```
Generating Embeddings for RAG System
Initializing embedding service...
Initializing vector store...
Loading data from database...
Found 5 schemes and 30 facts
Preparing documents for embedding...
Prepared 30 documents for embedding
Generating embeddings...
Processing batch 1/1
Generated 30 embeddings
Storing embeddings in vector database...
✓ Successfully stored all embeddings
Vector store now contains 30 documents
```

### 3. Run the Server

```bash
python run_server.py
```

The server will automatically use RAG if embeddings are available.

## How RAG Works

### 1. Query Processing
- User query is converted to an embedding vector
- Intent is extracted using LLM

### 2. Semantic Search
- Query embedding is compared with stored document embeddings
- Top-K most similar documents are retrieved (default: 5)
- Results are ranked by similarity score

### 3. Context Augmentation
- Retrieved documents are formatted into context
- Context includes: scheme name, fact type, value, source URL

### 4. Response Generation
- LLM generates response using retrieved context
- Response includes source URLs from retrieved documents

## Benefits of RAG

1. **Semantic Understanding**: Finds relevant information even with different wording
2. **Better Context**: Retrieves most relevant facts based on meaning, not just keywords
3. **Flexible Queries**: Handles queries that don't match exact scheme names
4. **Scalable**: Can handle large amounts of data efficiently

## Fallback Behavior

If RAG is not available (embeddings not generated), the system automatically falls back to:
- Traditional database queries
- Fuzzy string matching
- Rule-based retrieval

## Vector Database Location

Embeddings are stored in: `vector_db/` directory (created automatically)

## Updating Embeddings

When new facts are added to the database:

1. Re-run the embedding generation script:
```bash
python scripts/generate_embeddings.py
```

2. The script will add new embeddings to the vector store

## Verification

Check if RAG is working:

```bash
# Health check
curl http://localhost:8000/api/health

# Should show: "rag_configured": true
```

## Troubleshooting

### Issue: "RAG retriever not available"
- **Solution**: Run `python scripts/generate_embeddings.py` first

### Issue: "No relevant information found"
- **Solution**: Check if embeddings were generated successfully
- Verify vector store has documents: Check `vector_db/` directory

### Issue: Slow embedding generation
- **Solution**: This is normal for first run. Embeddings are cached in ChromaDB

## Performance

- **Embedding Generation**: ~1-2 seconds per batch of 32 documents
- **Vector Search**: <100ms for query retrieval
- **Total Response Time**: ~1-3 seconds (including LLM generation)

## Next Steps

1. Generate embeddings: `python scripts/generate_embeddings.py`
2. Start server: `python run_server.py`
3. Test queries: Use the API or test script
4. Monitor performance: Check logs for RAG retrieval stats

