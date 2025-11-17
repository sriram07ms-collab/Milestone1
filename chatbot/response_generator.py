"""Response generation using LLM"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from chatbot.llm_client import GeminiLLMClient, LLMQuotaExceededError
from chatbot.query_processor import QueryProcessor
from chatbot.advice_detector import is_investment_advice_query, get_facts_only_response, EDUCATIONAL_LINKS
from database.models import Scheme, SchemeFact

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generate responses to user queries"""
    
    def __init__(self, llm_client: GeminiLLMClient):
        self.llm_client = llm_client
    
    def format_fact_data(self, scheme: Scheme, facts: list) -> str:
        """Format scheme and fact data for LLM prompt"""
        lines = [f"Scheme: {scheme.scheme_name}"]
        lines.append(f"Category: {scheme.category or 'N/A'}")
        lines.append(f"Risk Level: {scheme.risk_level or 'N/A'}")
        lines.append(f"NAV: ₹{scheme.nav or 'N/A'}")
        lines.append(f"Expense Ratio: {scheme.expense_ratio or 'N/A'}")
        lines.append(f"Rating: {scheme.rating or 'N/A'}/5")
        lines.append(f"Fund Size: ₹{scheme.fund_size_cr or 'N/A'} Cr")
        lines.append(f"Source URL: {scheme.groww_url}")
        lines.append("")
        lines.append("Facts:")
        
        fact_map = {}
        for fact in facts:
            fact_map[fact.fact_type] = {
                "value": fact.fact_value,
                "source_url": fact.source_url
            }
        
        fact_descriptions = {
            "expense_ratio": "Expense Ratio",
            "exit_load": "Exit Load",
            "min_sip": "Minimum SIP",
            "min_lumpsum": "Minimum Lumpsum Investment",
            "lock_in_period": "Lock-in Period",
            "riskometer": "Riskometer",
            "benchmark": "Benchmark",
            "statement_download": "Statement Download Instructions"
        }
        
        for fact_type, description in fact_descriptions.items():
            if fact_type in fact_map:
                fact_data = fact_map[fact_type]
                lines.append(f"  {description}: {fact_data['value']}")
                lines.append(f"    Source: {fact_data['source_url']}")
        
        return "\n".join(lines)
    
    def generate_response(self, query: str, intent: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate response to user query
        
        Returns:
            Dictionary with:
            - answer: Generated answer
            - source_url: Source URL for the answer
            - scheme_name: Scheme name (if applicable)
            - fact_type: Type of fact answered
        """
        # Check for investment advice queries first
        is_advice, category = is_investment_advice_query(query)
        if is_advice:
            logger.info(f"Detected investment advice query, category: {category}")
            facts_only_response = get_facts_only_response(category)
            return {
                "answer": facts_only_response,
                "source_url": EDUCATIONAL_LINKS.get(category, EDUCATIONAL_LINKS['general']),
                "scheme_name": None,
                "fact_type": "general",
                "query_type": "general"
            }
        
        scheme = data.get("scheme")
        facts = data.get("facts", [])
        schemes = data.get("schemes", [])
        
        intent_type = intent.get("intent_type", "general")
        query_type = intent.get("query_type", "general")
        
        # Check if we have RAG context
        retrieved_context = data.get("retrieved_context")
        retrieved_docs = data.get("retrieved_docs", [])
        use_rag = retrieved_context is not None and len(retrieved_docs) > 0
        
        # Get last updated date
        last_updated = None
        if facts:
            last_updated = facts[0].extraction_date if hasattr(facts[0], 'extraction_date') else None
        elif retrieved_docs:
            # Try to get from metadata
            metadata = retrieved_docs[0].get('metadata', {})
            if 'extraction_date' in metadata:
                last_updated = metadata['extraction_date']
        
        # Build prompt with strict instructions
        if use_rag:
            # Use RAG context for better semantic understanding
            prompt = f"""You are a factual FAQ assistant for ICICI Prudential Mutual Funds on Groww platform.

User Question: "{query}"

Retrieved Context (from semantic search):
{retrieved_context}

CRITICAL INSTRUCTIONS:
1. Answer in MAXIMUM 3 sentences - be extremely concise
2. Use ONLY information from the retrieved context above
3. Do NOT provide investment advice, recommendations, or comparisons
4. Do NOT compute or compare returns
5. If information is not in context, say "Information not available"

Answer the user's question about {intent_type.replace('_', ' ')} in 3 sentences or less."""
        
        elif scheme and facts:
            # Specific fund query (fallback to traditional method)
            fact_data = self.format_fact_data(scheme, facts)
            
            # Find relevant fact
            relevant_fact = None
            for fact in facts:
                if fact.fact_type == intent_type:
                    relevant_fact = fact
                    break
            
            prompt = f"""You are a factual FAQ assistant for ICICI Prudential Mutual Funds on Groww platform.

User Question: "{query}"

Available Data:
{fact_data}

CRITICAL INSTRUCTIONS:
1. Answer in MAXIMUM 3 sentences - be extremely concise
2. Use ONLY information from the provided data above
3. Do NOT provide investment advice, recommendations, or comparisons
4. Do NOT compute or compare returns
5. If information is not available, say "Information not available for this scheme"

Answer the user's question about {intent_type.replace('_', ' ')} in 3 sentences or less."""
            
        elif schemes and facts:
            # Category query
            schemes_info = []
            for s in schemes[:5]:  # Limit to 5 schemes
                scheme_facts = [f for f in facts if f.scheme_id == s.scheme_id]
                if scheme_facts:
                    schemes_info.append(self.format_fact_data(s, scheme_facts))
            
            schemes_text = "\n\n---\n\n".join(schemes_info)
            
            prompt = f"""You are a factual FAQ assistant for ICICI Prudential Mutual Funds on Groww platform.

User Question: "{query}"

Available Data for Multiple Schemes:
{schemes_text}

CRITICAL INSTRUCTIONS:
1. Answer in MAXIMUM 3 sentences - be extremely concise
2. Use ONLY information from the provided data above
3. Do NOT provide investment advice, recommendations, or comparisons
4. Do NOT compute or compare returns
5. If multiple schemes, mention key facts only

Answer the user's question about {intent_type.replace('_', ' ')} in 3 sentences or less."""
        
        else:
            # General query
            prompt = f"""You are a factual FAQ assistant for ICICI Prudential Mutual Funds on Groww platform.

User Question: "{query}"

CRITICAL INSTRUCTIONS:
1. Answer in MAXIMUM 3 sentences - be extremely concise
2. Provide factual information only - do NOT provide investment advice
3. Do NOT compute or compare returns
4. If specific scheme info needed, ask user to specify scheme name
5. For statement downloads, provide general Groww account access instructions

Answer the user's question in 3 sentences or less."""
        
        try:
            # Generate response
            answer = self.llm_client.generate_response(prompt, temperature=0.3)
            
            # Ensure answer is concise (max 3 sentences)
            sentences = [s.strip() for s in answer.split('.') if s.strip()]
            if len(sentences) > 3:
                answer = '. '.join(sentences[:3]) + '.'
            
            # Extract source URL from answer or use retrieved/fallback URL
            source_url = None
            if retrieved_docs:
                # Use source URL from most relevant retrieved document
                source_url = retrieved_docs[0].get('metadata', {}).get('source_url')
            elif scheme:
                source_url = scheme.groww_url
            elif facts and len(facts) > 0:
                source_url = facts[0].source_url
            
            # Parse answer to extract source URL if mentioned
            import re
            url_match = re.search(r'https?://[^\s]+', answer)
            if url_match:
                source_url = url_match.group(0)
            
            # Ensure we have a valid source URL
            if not source_url:
                source_url = "https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds"
            
            return {
                "answer": answer,
                "source_url": source_url,
                "scheme_name": scheme.scheme_name if scheme else None,
                "fact_type": intent_type,
                "query_type": query_type
            }
            
        except LLMQuotaExceededError as e:
            logger.warning(f"LLM quota exceeded while generating response: {e}")
            return self._generate_fallback_answer(
                intent_type,
                query_type,
                scheme,
                facts,
                retrieved_docs,
                quota_limited=True
            )
        except Exception as e:
            logger.error(f"Error generating response from LLM: {e}")
            return self._generate_fallback_answer(
                intent_type,
                query_type,
                scheme,
                facts,
                retrieved_docs,
                quota_limited=False
            )

    def _generate_fallback_answer(
        self,
        intent_type: str,
        query_type: str,
        scheme,
        facts,
        retrieved_docs,
        quota_limited: bool = False
    ) -> Dict[str, Any]:
        """
        Build a fallback answer using stored data.
        """
        logger.info("Attempting fallback to stored data")
        preface = ""
        if quota_limited:
            preface = "Temporarily exceeded LLM quota; sharing stored facts instead. "
        
        # Fallback: Use RAG data directly if available
        if retrieved_docs and len(retrieved_docs) > 0:
            try:
                answer_parts = []
                fact_descriptions = {
                    "expense_ratio": "Expense Ratio",
                    "exit_load": "Exit Load",
                    "min_sip": "Minimum SIP",
                    "min_lumpsum": "Minimum Lumpsum Investment",
                    "lock_in_period": "Lock-in Period",
                    "riskometer": "Riskometer",
                    "benchmark": "Benchmark",
                    "statement_download": "Statement Download Instructions"
                }
                
                for doc in retrieved_docs[:3]:
                    metadata = doc.get('metadata', {})
                    fact_type = metadata.get('fact_type', '')
                    fact_value = metadata.get('fact_value', '')
                    scheme_name = metadata.get('scheme_name', '')
                    
                    if fact_value and scheme_name:
                        fact_label = fact_descriptions.get(fact_type, fact_type.replace('_', ' ').title())
                        answer_parts.append(f"{scheme_name}: {fact_label} is {fact_value}")
                
                if answer_parts:
                    if len(answer_parts) == 1:
                        answer = answer_parts[0]
                    else:
                        limited_parts = answer_parts[:3]
                        answer = ". ".join(limited_parts) + "."
                    
                    answer = f"{preface}{answer}".strip()
                    source_url = retrieved_docs[0].get('metadata', {}).get('source_url')
                    scheme_name = retrieved_docs[0].get('metadata', {}).get('scheme_name')
                    
                    logger.info("Fallback answer generated from RAG data")
                    return {
                        "answer": answer,
                        "source_url": source_url or "https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds",
                        "scheme_name": scheme_name,
                        "fact_type": intent_type,
                        "query_type": query_type
                    }
            except Exception as fallback_error:
                logger.error(f"Error in RAG fallback: {fallback_error}")
        
        # Fallback: Use database facts if available
        if facts and len(facts) > 0:
            try:
                relevant_fact = None
                for fact in facts:
                    if fact.fact_type == intent_type:
                        relevant_fact = fact
                        break
                
                if not relevant_fact:
                    relevant_fact = facts[0]
                
                if relevant_fact:
                    fact_descriptions = {
                        "expense_ratio": "Expense Ratio",
                        "exit_load": "Exit Load",
                        "min_sip": "Minimum SIP",
                        "min_lumpsum": "Minimum Lumpsum Investment",
                        "lock_in_period": "Lock-in Period",
                        "riskometer": "Riskometer",
                        "benchmark": "Benchmark",
                        "statement_download": "Statement Download Instructions"
                    }
                    
                    fact_label = fact_descriptions.get(relevant_fact.fact_type, relevant_fact.fact_type.replace('_', ' ').title())
                    scheme_name_str = scheme.scheme_name if scheme else "ICICI Prudential Mutual Fund"
                    answer = f"{scheme_name_str}: {fact_label} is {relevant_fact.fact_value}"
                    answer = f"{preface}{answer}".strip()
                    
                    logger.info("Fallback answer generated from database facts")
                    return {
                        "answer": answer,
                        "source_url": relevant_fact.source_url or (scheme.groww_url if scheme else "https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds"),
                        "scheme_name": scheme.scheme_name if scheme else None,
                        "fact_type": intent_type,
                        "query_type": query_type
                    }
            except Exception as db_fallback_error:
                logger.error(f"Error in database fallback: {db_fallback_error}")
        
        logger.warning("Fallback failed; returning generic error message")
        generic_message = "I couldn't access the answer service right now. Please try again in a few minutes."
        if quota_limited:
            generic_message = "Temporarily exceeded daily limits. Please try again shortly."
        
        return {
            "answer": generic_message,
            "source_url": "https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds",
            "scheme_name": None,
            "fact_type": intent_type,
            "query_type": query_type
        }

