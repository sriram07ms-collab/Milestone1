"""API routes"""
import logging
import os
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from api.schemas import (
    ChatRequest, ChatResponse, SchemeDetailResponse,
    SchemesListResponse, HealthResponse, SchemeInfo, SchemeFactInfo
)
from chatbot.query_processor import QueryProcessor
from chatbot.response_generator import ResponseGenerator
from chatbot.llm_client import GeminiLLMClient
from rag.embedding_service import EmbeddingService
from rag.vector_store import VectorStore
from rag.rag_retriever import RAGRetriever
from database.models import Scheme, SchemeFact
from database.db_connection import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize LLM client and RAG components (singletons)
_llm_client = None
_embedding_service = None
_vector_store = None
_rag_retriever = None
_query_processor = None
_response_generator = None


def get_llm_client() -> GeminiLLMClient:
    """Get or create LLM client"""
    global _llm_client
    if _llm_client is None:
        try:
            _llm_client = GeminiLLMClient()
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise HTTPException(status_code=500, detail="LLM service unavailable")
    return _llm_client


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service"""
    global _embedding_service
    if _embedding_service is None:
        try:
            _embedding_service = EmbeddingService()
        except Exception as e:
            logger.warning(f"Failed to initialize embedding service: {e}")
    return _embedding_service


def get_vector_store() -> VectorStore:
    """Get or create vector store"""
    global _vector_store
    if _vector_store is None:
        try:
            _vector_store = VectorStore()
        except Exception as e:
            logger.warning(f"Failed to initialize vector store: {e}")
    return _vector_store


def get_rag_retriever() -> RAGRetriever:
    """Get or create RAG retriever"""
    global _rag_retriever
    if _rag_retriever is None:
        try:
            embedding_service = get_embedding_service()
            vector_store = get_vector_store()
            if embedding_service and vector_store:
                _rag_retriever = RAGRetriever(embedding_service, vector_store)
                logger.info("RAG retriever initialized successfully")
            else:
                logger.warning("RAG retriever not available - missing dependencies")
        except Exception as e:
            logger.warning(f"Failed to initialize RAG retriever: {e}")
    return _rag_retriever


def get_query_processor() -> QueryProcessor:
    """Get or create query processor"""
    global _query_processor
    if _query_processor is None:
        llm_client = get_llm_client()
        rag_retriever = get_rag_retriever()  # Try to get RAG retriever
        _query_processor = QueryProcessor(llm_client, rag_retriever=rag_retriever)
    return _query_processor


def get_response_generator() -> ResponseGenerator:
    """Get or create response generator"""
    global _response_generator
    if _response_generator is None:
        llm_client = get_llm_client()
        _response_generator = ResponseGenerator(llm_client)
    return _response_generator


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for FAQ queries
    
    Accepts user questions about ICICI Prudential mutual funds and returns
    factual answers with source URLs.
    """
    try:
        query_processor = get_query_processor()
        response_generator = get_response_generator()
        
        # Extract intent
        intent = query_processor.extract_intent(request.query)
        
        # Get relevant data using RAG (semantic search)
        data = query_processor.get_relevant_data(request.query, intent)
        
        # Generate response
        response = response_generator.generate_response(
            request.query,
            intent,
            data
        )
        
        # Get last updated date from facts if available
        last_updated = None
        if data.get("facts"):
            last_updated = data["facts"][0].extraction_date
        
        return ChatResponse(
            answer=response["answer"],
            source_url=response["source_url"],
            scheme_name=response.get("scheme_name"),
            fact_type=response.get("fact_type"),
            query_type=response.get("query_type"),
            last_updated=last_updated
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@router.get("/schemes", response_model=SchemesListResponse)
async def list_schemes():
    """Get list of all ICICI Prudential schemes"""
    try:
        with get_db_session() as db:
            schemes = db.query(Scheme).all()
            scheme_info = [
                SchemeInfo(
                    scheme_id=s.scheme_id,
                    scheme_name=s.scheme_name,
                    category=s.category,
                    risk_level=s.risk_level,
                    nav=s.nav,
                    expense_ratio=s.expense_ratio,
                    rating=s.rating,
                    fund_size_cr=s.fund_size_cr,
                    groww_url=s.groww_url
                )
                for s in schemes
            ]
        
        return SchemesListResponse(
            schemes=scheme_info,
            total=len(scheme_info)
        )
    except Exception as e:
        logger.error(f"Error listing schemes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schemes/{scheme_id}", response_model=SchemeDetailResponse)
async def get_scheme_details(scheme_id: int):
    """Get detailed information about a specific scheme"""
    try:
        with get_db_session() as db:
            scheme = db.query(Scheme).filter_by(scheme_id=scheme_id).first()
            if not scheme:
                raise HTTPException(status_code=404, detail="Scheme not found")
            
            facts = db.query(SchemeFact).filter_by(
                scheme_id=scheme_id,
                is_active=True
            ).all()
            
            scheme_info = SchemeInfo(
                scheme_id=scheme.scheme_id,
                scheme_name=scheme.scheme_name,
                category=scheme.category,
                risk_level=scheme.risk_level,
                nav=scheme.nav,
                expense_ratio=scheme.expense_ratio,
                rating=scheme.rating,
                fund_size_cr=scheme.fund_size_cr,
                groww_url=scheme.groww_url
            )
            
            fact_info = [
                SchemeFactInfo(
                    fact_id=f.fact_id,
                    fact_type=f.fact_type,
                    fact_value=f.fact_value,
                    source_url=f.source_url,
                    extraction_date=f.extraction_date
                )
                for f in facts
            ]
        
        return SchemeDetailResponse(
            scheme=scheme_info,
            facts=fact_info
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scheme details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        db_connected = False
        try:
            with get_db_session() as db:
                db.query(Scheme).first()
                db_connected = True
        except Exception:
            pass
        
        # Check LLM
        llm_configured = False
        try:
            get_llm_client()
            llm_configured = True
        except Exception:
            pass
        
        # Check RAG system (optional; avoid heavy init on health)
        rag_configured = False
        rag_enabled = os.getenv("RAG_ENABLED", "false").lower() in ("1", "true", "yes")
        if rag_enabled:
            try:
                rag_retriever = get_rag_retriever()
                if rag_retriever:
                    vector_store = get_vector_store()
                    if vector_store and vector_store.get_count() > 0:
                        rag_configured = True
            except Exception:
                pass
        
        status = "healthy" if (db_connected and llm_configured) else "degraded"
        message = "All systems operational" if status == "healthy" else "Some services unavailable"
        if rag_configured:
            message += " (RAG enabled)"
        
        return HealthResponse(
            status=status,
            message=message,
            database_connected=db_connected,
            llm_configured=llm_configured,
            rag_configured=rag_configured
        )
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return HealthResponse(
            status="error",
            message=str(e),
            database_connected=False,
            llm_configured=False,
            rag_configured=False
        )

