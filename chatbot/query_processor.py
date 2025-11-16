"""Query processing and intent extraction"""
import logging
from typing import Dict, Any, Optional, List
from chatbot.llm_client import GeminiLLMClient
from chatbot.scheme_matcher import SchemeMatcher
from rag.rag_retriever import RAGRetriever
from database.models import Scheme, SchemeFact, SessionLocal

logger = logging.getLogger(__name__)


class QueryProcessor:
    """Process user queries and extract intent"""
    
    def __init__(self, llm_client: GeminiLLMClient, rag_retriever: Optional[RAGRetriever] = None):
        self.llm_client = llm_client
        self.scheme_matcher = SchemeMatcher()
        self.session = SessionLocal()
        self.rag_retriever = rag_retriever
        self.use_rag = rag_retriever is not None
    
    def extract_intent(self, query: str) -> Dict[str, Any]:
        """
        Extract intent from user query using LLM
        
        Returns:
            Dictionary with:
            - intent_type: expense_ratio, exit_load, min_sip, etc.
            - scheme_name: Extracted scheme name (if any)
            - query_type: specific_fund, category_query, general
        """
        prompt = f"""You are a query understanding system for a mutual fund FAQ assistant.

User Query: "{query}"

Analyze this query and extract:
1. What information is the user asking about? (expense_ratio, exit_load, min_sip, min_lumpsum, lock_in_period, riskometer, benchmark, statement_download, or general)
2. Which ICICI Prudential mutual fund scheme is mentioned? (extract the scheme name if present)
3. What type of query is this? (specific_fund, category_query, general)

Respond in JSON format:
{{
    "intent_type": "expense_ratio|exit_load|min_sip|min_lumpsum|lock_in_period|riskometer|benchmark|statement_download|general",
    "scheme_name": "extracted scheme name or null",
    "query_type": "specific_fund|category_query|general",
    "category": "Large Cap|Mid Cap|Small Cap or null if not mentioned"
}}

Examples:
- "What is the expense ratio of ICICI Prudential Large Cap Fund?" -> {{"intent_type": "expense_ratio", "scheme_name": "ICICI Prudential Large Cap Fund", "query_type": "specific_fund", "category": null}}
- "What is the minimum SIP for mid cap funds?" -> {{"intent_type": "min_sip", "scheme_name": null, "query_type": "category_query", "category": "Mid Cap"}}
- "How to download statements?" -> {{"intent_type": "statement_download", "scheme_name": null, "query_type": "general", "category": null}}
"""
        
        try:
            intent = self.llm_client.generate_structured_response(prompt, temperature=0.3)
            logger.info(f"Extracted intent: {intent}")
            return intent
        except Exception as e:
            logger.error(f"Error extracting intent: {e}")
            # Fallback to simple pattern matching
            return self._fallback_intent_extraction(query)
    
    def _fallback_intent_extraction(self, query: str) -> Dict[str, Any]:
        """Fallback intent extraction using pattern matching"""
        query_lower = query.lower()
        
        intent_type = "general"
        if "expense ratio" in query_lower or "expense" in query_lower:
            intent_type = "expense_ratio"
        elif "exit load" in query_lower:
            intent_type = "exit_load"
        elif "minimum sip" in query_lower or "min sip" in query_lower:
            intent_type = "min_sip"
        elif "minimum lumpsum" in query_lower or "min lumpsum" in query_lower:
            intent_type = "min_lumpsum"
        elif "lock" in query_lower or "lock-in" in query_lower:
            intent_type = "lock_in_period"
        elif "risk" in query_lower or "riskometer" in query_lower:
            intent_type = "riskometer"
        elif "benchmark" in query_lower:
            intent_type = "benchmark"
        elif "statement" in query_lower or "download" in query_lower:
            intent_type = "statement_download"
        
        # Try to match scheme
        scheme = self.scheme_matcher.find_matching_scheme(query)
        scheme_name = scheme.scheme_name if scheme else None
        
        return {
            "intent_type": intent_type,
            "scheme_name": scheme_name,
            "query_type": "specific_fund" if scheme_name else "general",
            "category": None
        }
    
    def get_relevant_data(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get relevant data using RAG (semantic search) or traditional database queries
        
        Returns:
            Dictionary with scheme, fact data, and retrieved context
        """
        data = {
            "scheme": None,
            "facts": [],
            "schemes": [],
            "retrieved_context": None,
            "retrieved_docs": []
        }
        
        intent_type = intent.get("intent_type", "general")
        scheme_name = intent.get("scheme_name")
        query_type = intent.get("query_type", "general")
        category = intent.get("category")
        
        # Use RAG if available
        if self.use_rag and self.rag_retriever:
            try:
                # Determine filters for RAG search
                scheme_id = None
                if scheme_name:
                    scheme = self.scheme_matcher.find_matching_scheme(scheme_name)
                    if scheme:
                        scheme_id = scheme.scheme_id
                        data["scheme"] = scheme
                
                # Retrieve using semantic search
                retrieved_docs = self.rag_retriever.retrieve(
                    query=query,
                    top_k=5,
                    scheme_id=scheme_id,
                    fact_type=intent_type if intent_type != "general" else None
                )
                
                data["retrieved_docs"] = retrieved_docs
                data["retrieved_context"] = self.rag_retriever.format_retrieved_context(retrieved_docs)
                
                # Also get full fact objects from database for metadata
                if retrieved_docs:
                    fact_ids = [doc['metadata'].get('fact_id') for doc in retrieved_docs if doc['metadata'].get('fact_id')]
                    if fact_ids:
                        facts = self.session.query(SchemeFact).filter(
                            SchemeFact.fact_id.in_(fact_ids)
                        ).all()
                        data["facts"] = facts
                
                logger.info(f"RAG retrieval found {len(retrieved_docs)} relevant documents")
                
            except Exception as e:
                logger.error(f"Error in RAG retrieval, falling back to database: {e}")
                self.use_rag = False  # Fallback to traditional method
        
        # Fallback to traditional database queries if RAG not available or failed
        if not self.use_rag or not data["retrieved_docs"]:
            # Find scheme(s)
            if query_type == "specific_fund" and scheme_name:
                scheme = self.scheme_matcher.find_matching_scheme(scheme_name)
                if scheme:
                    data["scheme"] = scheme
                    # Get facts for this scheme
                    facts = self.session.query(SchemeFact).filter_by(
                        scheme_id=scheme.scheme_id,
                        is_active=True
                    ).all()
                    data["facts"] = facts
            
            elif query_type == "category_query" and category:
                schemes = self.scheme_matcher.find_schemes_by_category(category)
                data["schemes"] = schemes
                # Get facts for all schemes in category
                for scheme in schemes:
                    facts = self.session.query(SchemeFact).filter_by(
                        scheme_id=scheme.scheme_id,
                        is_active=True
                    ).all()
                    data["facts"].extend(facts)
            
            else:
                # General query - get all schemes
                schemes = self.scheme_matcher._get_all_schemes()
                data["schemes"] = schemes
        
        return data
    
    def close(self):
        """Close database session"""
        if self.session:
            self.session.close()
        if self.scheme_matcher:
            self.scheme_matcher.close()
        if self.rag_retriever:
            self.rag_retriever.close()

