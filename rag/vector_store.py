"""Vector store for storing and retrieving embeddings"""
import logging
import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from pathlib import Path
from config.settings import BASE_DIR

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store using ChromaDB for semantic search"""
    
    def __init__(self, collection_name: str = "icici_funds", persist_directory: Optional[str] = None):
        """
        Initialize vector store
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist data (defaults to BASE_DIR/vector_db)
        """
        if persist_directory is None:
            persist_directory = str(BASE_DIR / "vector_db")
        
        # Create directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "ICICI Prudential Mutual Fund facts and schemes"}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        self.collection_name = collection_name
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """
        Add documents to the vector store
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of unique IDs for each document
        """
        if len(documents) != len(embeddings) != len(metadatas) != len(ids):
            raise ValueError("All lists must have the same length")
        
        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Dictionary with 'ids', 'documents', 'metadatas', 'distances'
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            return results
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    def search_by_text(
        self,
        query_text: str,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search by text (uses embedding for semantic search)
        
        Args:
            query_text: Query text
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Dictionary with 'ids', 'documents', 'metadatas', 'distances'
        """
        return self.search(query_embedding, n_results, where)
    
    def delete(self, ids: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None):
        """
        Delete documents from the vector store
        
        Args:
            ids: List of IDs to delete
            where: Metadata filter for deletion
        """
        try:
            self.collection.delete(ids=ids, where=where)
            logger.info(f"Deleted documents from vector store")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    def get_count(self) -> int:
        """Get total number of documents in the collection"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error getting count: {e}")
            return 0
    
    def reset(self):
        """Reset the collection (delete all documents)"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "ICICI Prudential Mutual Fund facts and schemes"}
            )
            logger.info("Reset vector store collection")
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            raise

