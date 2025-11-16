"""Detect investment advice questions"""
import re
from typing import Tuple

# Patterns that indicate investment advice requests
ADVICE_PATTERNS = [
    # Direct investment advice
    r'\b(should|must|need to|recommend|suggest|advise)\b.*\b(invest|fund|scheme|plan)\b',
    r'\b(best|top|worst)\b.*\b(fund|scheme|elss|equity|debt|hybrid)\b.*\b(invest|put|choose)\b',
    r'\b(which|what)\b.*\b(fund|scheme)\b.*\b(invest|choose|pick|select|should)\b',
    r'\b(which|what)\b.*\b(should|must|need to)\b.*\b(invest|fund|scheme)\b',
    
    # Timing advice
    r'\b(good time|right time|best time|when|timing)\b.*\b(invest|buy|sell)\b',
    r'\b(should.*now|should.*wait|when.*invest|is.*time)\b',
    r'\b(is it|is this)\b.*\b(good|right|best)\b.*\b(time|moment)\b.*\b(invest|buy)\b',
    
    # Comparison advice
    r'\b(better|worse|compare|comparison|vs|versus)\b.*\b(fund|scheme)\b.*\b(choose|select|should)\b',
    r'\b(which.*better|which.*choose|which.*prefer|which.*should)\b',
    r'\b(is|are)\b.*\b(better|worse|good|bad)\b.*\b(than|or)\b',
    
    # Returns/performance advice
    r'\b(returns|performance|profit|gain|loss)\b.*\b(next|future|coming|5 years|10 years|will give)\b',
    r'\b(highest|lowest|best|worst)\b.*\b(returns|performance)\b',
    r'\b(will give|will provide|will earn)\b.*\b(returns|profit)\b',
    
    # Portfolio advice
    r'\b(portfolio|allocation|diversification|how much|how many)\b.*\b(invest|allocate|should)\b',
    
    # Tax advice
    r'\b(tax|tax saving|tax benefit|elss)\b.*\b(invest|choose|best|should)\b',
    r'\b(best|top)\b.*\b(elss|tax saving)\b',
    
    # Suitability advice
    r'\b(suitable|right for|good for|fit for)\b.*\b(me|my|i|retirement|goal)\b',
    r'\b(should i|what should|what.*for me|for my)\b',
    
    # Shift/switch advice
    r'\b(shift|switch|change|transfer|move)\b.*\b(from|to|plan|fund)\b.*\b(should|now)\b',
    r'\b(should.*shift|should.*switch|should.*change)\b',
    
    # Risk advice
    r'\b(risk|risky|safe|secure)\b.*\b(invest|fund|scheme)\b.*\b(should|recommend)\b',
    
    # Bypass attempts - queries trying to get advice by saying they won't consider it advice
    r'\b(just tell|just say|just recommend|just suggest)\b.*\b(good|best|better)\b',
    r'\b(won.*t|will not|don.*t|do not)\b.*\b(consider|treat|take)\b.*\b(advice)\b',
    r'\b(which.*good|what.*good|tell.*good|say.*good)\b.*\b(won.*t|will not|don.*t|do not)\b',
    r'\b(fund|scheme)\b.*\b(good|best|better)\b.*\b(won.*t|will not|don.*t|do not)\b.*\b(advice)\b',
]

# Educational links for different topics
EDUCATIONAL_LINKS = {
    'general': 'https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds',
    'elss': 'https://groww.in/mutual-funds/elss',
    'equity': 'https://groww.in/mutual-funds/equity',
    'debt': 'https://groww.in/mutual-funds/debt',
    'hybrid': 'https://groww.in/mutual-funds/hybrid',
    'returns': 'https://groww.in/mutual-funds',
    'tax': 'https://groww.in/mutual-funds/elss',
    'portfolio': 'https://groww.in/mutual-funds',
}


def is_investment_advice_query(query: str) -> Tuple[bool, str]:
    """
    Detect if query is asking for investment advice
    
    Returns:
        Tuple of (is_advice, category)
    """
    query_lower = query.lower()
    
    # Check against patterns
    for pattern in ADVICE_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            # Determine category for educational link
            category = 'general'
            if 'elss' in query_lower or 'tax' in query_lower:
                category = 'elss'
            elif 'equity' in query_lower:
                category = 'equity'
            elif 'debt' in query_lower:
                category = 'debt'
            elif 'hybrid' in query_lower:
                category = 'hybrid'
            elif 'return' in query_lower or 'performance' in query_lower:
                category = 'returns'
            elif 'portfolio' in query_lower or 'allocation' in query_lower:
                category = 'portfolio'
            
            return True, category
    
    return False, 'general'


def get_facts_only_response(category: str = 'general') -> str:
    """Get polite facts-only response for investment advice queries"""
    educational_link = EDUCATIONAL_LINKS.get(category, EDUCATIONAL_LINKS['general'])
    
    response = (
        "I provide factual information about mutual fund schemes only, not investment advice. "
        "For investment decisions, please consult a registered investment advisor. "
        f"Learn more: {educational_link}"
    )
    
    return response

