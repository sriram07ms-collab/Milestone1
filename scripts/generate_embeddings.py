"""Script to generate and store embeddings for all facts"""
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.embedding_service import EmbeddingService
from rag.vector_store import VectorStore
from database.models import Scheme, SchemeFact, SessionLocal, init_db
from database.db_connection import get_db_session

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def generate_document_text(scheme: Scheme, fact: SchemeFact) -> str:
    """Generate document text for embedding"""
    parts = []
    
    # Scheme information
    parts.append(f"Scheme: {scheme.scheme_name}")
    if scheme.category:
        parts.append(f"Category: {scheme.category}")
    if scheme.risk_level:
        parts.append(f"Risk Level: {scheme.risk_level}")
    
    # Fact information
    fact_descriptions = {
        "expense_ratio": "Expense Ratio",
        "exit_load": "Exit Load",
        "min_sip": "Minimum SIP Investment",
        "min_lumpsum": "Minimum Lumpsum Investment",
        "lock_in_period": "Lock-in Period",
        "riskometer": "Riskometer",
        "benchmark": "Benchmark",
        "statement_download": "Statement Download Instructions"
    }
    
    fact_label = fact_descriptions.get(fact.fact_type, fact.fact_type.replace('_', ' ').title())
    parts.append(f"{fact_label}: {fact.fact_value}")
    
    return " | ".join(parts)


def main():
    """Generate embeddings for all facts and store in vector database"""
    logger.info("=" * 80)
    logger.info("Generating Embeddings for RAG System")
    logger.info("=" * 80)
    
    # Initialize services
    logger.info("Initializing embedding service...")
    embedding_service = EmbeddingService()
    
    logger.info("Initializing vector store...")
    vector_store = VectorStore()
    
    # Reset vector store (optional - comment out if you want to keep existing data)
    # vector_store.reset()
    
    # Get all schemes and facts from database
    logger.info("Loading data from database...")
    with get_db_session() as db:
        schemes = db.query(Scheme).all()
        facts = db.query(SchemeFact).filter_by(is_active=True).all()
        
        # Create scheme lookup while session is active
        scheme_lookup = {}
        for s in schemes:
            # Access all attributes while session is open
            scheme_lookup[s.scheme_id] = {
                'scheme_id': s.scheme_id,
                'scheme_name': s.scheme_name,
                'category': s.category,
                'risk_level': s.risk_level,
                'groww_url': s.groww_url
            }
        
        # Extract fact data while session is active
        facts_data = []
        for f in facts:
            facts_data.append({
                'scheme_id': f.scheme_id,
                'fact_id': f.fact_id,
                'fact_type': f.fact_type,
                'fact_value': f.fact_value,
                'source_url': f.source_url,
                'extraction_date': f.extraction_date
            })
    
    logger.info(f"Found {len(schemes)} schemes and {len(facts_data)} facts")
    
    # Prepare documents for embedding
    documents = []
    metadatas = []
    ids = []
    
    logger.info("Preparing documents for embedding...")
    for fact_data in facts_data:
        scheme_data = scheme_lookup.get(fact_data['scheme_id'])
        if not scheme_data:
            continue
        
        # Create a simple scheme-like object for the function
        class SchemeData:
            def __init__(self, data):
                self.scheme_name = data['scheme_name']
                self.category = data['category']
                self.risk_level = data['risk_level']
        
        class FactData:
            def __init__(self, data):
                self.fact_type = data['fact_type']
                self.fact_value = data['fact_value']
        
        scheme_obj = SchemeData(scheme_data)
        fact_obj = FactData(fact_data)
        
        # Generate document text
        doc_text = generate_document_text(scheme_obj, fact_obj)
        
        # Create metadata
        metadata = {
            "scheme_id": fact_data['scheme_id'],
            "scheme_name": scheme_data['scheme_name'],
            "fact_id": fact_data['fact_id'],
            "fact_type": fact_data['fact_type'],
            "fact_value": fact_data['fact_value'],
            "source_url": fact_data['source_url'],
            "category": scheme_data['category'] or "",
            "extraction_date": str(fact_data['extraction_date'])
        }
        
        # Create unique ID
        doc_id = f"scheme_{fact_data['scheme_id']}_fact_{fact_data['fact_id']}_{fact_data['fact_type']}"
        
        documents.append(doc_text)
        metadatas.append(metadata)
        ids.append(doc_id)
    
    logger.info(f"Prepared {len(documents)} documents for embedding")
    
    # Generate embeddings in batches
    logger.info("Generating embeddings...")
    batch_size = 32
    embeddings = []
    
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
        
        batch_embeddings = embedding_service.generate_embeddings_batch(batch_docs, batch_size=batch_size)
        embeddings.extend(batch_embeddings)
    
    logger.info(f"Generated {len(embeddings)} embeddings")
    
    # Store in vector database
    logger.info("Storing embeddings in vector database...")
    try:
        vector_store.add_documents(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        logger.info("✓ Successfully stored all embeddings")
    except Exception as e:
        logger.error(f"Error storing embeddings: {e}")
        raise
    
    # Verify
    count = vector_store.get_count()
    logger.info(f"Vector store now contains {count} documents")
    
    logger.info("=" * 80)
    logger.info("Embedding generation completed!")
    logger.info("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

