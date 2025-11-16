"""RAG retriever for semantic search"""
import logging
from typing import List, Dict, Any, Optional
from rag.embedding_service import EmbeddingService
from rag.vector_store import VectorStore
from database.models import Scheme, SchemeFact, SessionLocal

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Retriever for RAG-based semantic search"""
    
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore):
        """
        Initialize RAG retriever
        
        Args:
            embedding_service: Service for generating embeddings
            vector_store: Vector store for semantic search
        """
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.session = SessionLocal()
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        scheme_id: Optional[int] = None,
        fact_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents using semantic search
        
        Args:
            query: User query
            top_k: Number of results to retrieve
            scheme_id: Optional filter by scheme ID
            fact_type: Optional filter by fact type
            
        Returns:
            List of retrieved documents with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query)
            
            # Build metadata filter
            where = {}
            if scheme_id:
                where["scheme_id"] = scheme_id
            if fact_type:
                where["fact_type"] = fact_type
            
            # Search vector store
            results = self.vector_store.search(
                query_embedding=query_embedding,
                n_results=top_k,
                where=where if where else None
            )
            
            # Format results
            retrieved_docs = []
            if results.get('ids') and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    doc = {
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i] if results.get('documents') else '',
                        'metadata': results['metadatas'][0][i] if results.get('metadatas') else {},
                        'distance': results['distances'][0][i] if results.get('distances') else 0.0,
                        'score': 1.0 - results['distances'][0][i] if results.get('distances') else 1.0
                    }
                    retrieved_docs.append(doc)
            
            logger.info(f"Retrieved {len(retrieved_docs)} documents for query: {query[:50]}...")
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def format_retrieved_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into context string for LLM
        
        Args:
            retrieved_docs: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return "No relevant information found."
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            metadata = doc.get('metadata', {})
            text = doc.get('text', '')
            
            context_part = f"[Document {i}]"
            if metadata.get('scheme_name'):
                context_part += f"\nScheme: {metadata['scheme_name']}"
            if metadata.get('fact_type'):
                context_part += f"\nFact Type: {metadata['fact_type']}"
            if metadata.get('fact_value'):
                context_part += f"\nValue: {metadata['fact_value']}"
            if metadata.get('source_url'):
                context_part += f"\nSource: {metadata['source_url']}"
            if text:
                context_part += f"\nContent: {text}"
            
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def close(self):
        """Close database session"""
        if self.session:
            self.session.close()

