"""Scheme name matching utilities"""
import logging
import re
from typing import List, Optional, Dict, Any
from database.models import Scheme, SessionLocal
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class SchemeMatcher:
    """Match user queries to scheme names"""
    
    def __init__(self):
        self.session = SessionLocal()
        self._schemes_cache = None
    
    def _get_all_schemes(self) -> List[Scheme]:
        """Get all schemes from database (with caching)"""
        if self._schemes_cache is None:
            self._schemes_cache = self.session.query(Scheme).all()
        return self._schemes_cache
    
    def normalize_scheme_name(self, name: str) -> str:
        """Normalize scheme name for matching"""
        # Remove common suffixes
        name = re.sub(r'\s*Direct\s*Plan\s*Growth\s*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*Direct\s*Growth\s*$', '', name, flags=re.IGNORECASE)
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())
        return name.lower()
    
    def extract_scheme_name_from_query(self, query: str) -> Optional[str]:
        """Extract potential scheme name from user query"""
        # Common patterns
        patterns = [
            r'ICICI\s+Prudential\s+([A-Za-z\s&]+?)(?:\s+Fund|\s+Direct|$)',
            r'ICICI\s+Prudential\s+([A-Za-z\s&]+)',
            r'([A-Za-z\s&]+?)\s+Fund\s+ICICI',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def find_matching_scheme(self, query: str, threshold: float = 0.6) -> Optional[Scheme]:
        """
        Find best matching scheme from query
        
        Args:
            query: User query
            threshold: Minimum similarity threshold (0.0 to 1.0)
            
        Returns:
            Best matching scheme or None
        """
        schemes = self._get_all_schemes()
        if not schemes:
            return None
        
        query_lower = query.lower()
        best_match = None
        best_score = 0.0
        
        # Extract potential scheme name
        extracted_name = self.extract_scheme_name_from_query(query)
        
        for scheme in schemes:
            # Normalize scheme name
            scheme_name_normalized = self.normalize_scheme_name(scheme.scheme_name)
            scheme_name_lower = scheme.scheme_name.lower()
            
            # Calculate similarity scores
            scores = []
            
            # 1. Direct substring match
            if query_lower in scheme_name_lower or scheme_name_lower in query_lower:
                scores.append(0.9)
            
            # 2. Sequence matcher similarity
            similarity = SequenceMatcher(None, query_lower, scheme_name_lower).ratio()
            scores.append(similarity)
            
            # 3. If extracted name exists, check against it
            if extracted_name:
                extracted_normalized = self.normalize_scheme_name(extracted_name)
                similarity_extracted = SequenceMatcher(None, extracted_normalized, scheme_name_normalized).ratio()
                scores.append(similarity_extracted)
            
            # 4. Check category match
            if scheme.category:
                category_lower = scheme.category.lower()
                if category_lower in query_lower:
                    scores.append(0.7)
            
            # Take maximum score
            max_score = max(scores) if scores else 0.0
            
            if max_score > best_score and max_score >= threshold:
                best_score = max_score
                best_match = scheme
        
        if best_match:
            logger.info(f"Matched query '{query}' to scheme '{best_match.scheme_name}' (score: {best_score:.2f})")
        
        return best_match
    
    def find_schemes_by_category(self, category: str) -> List[Scheme]:
        """Find all schemes in a category"""
        schemes = self._get_all_schemes()
        category_lower = category.lower()
        
        matching = []
        for scheme in schemes:
            if scheme.category and category_lower in scheme.category.lower():
                matching.append(scheme)
        
        return matching
    
    def get_all_scheme_names(self) -> List[str]:
        """Get list of all scheme names"""
        schemes = self._get_all_schemes()
        return [scheme.scheme_name for scheme in schemes]
    
    def close(self):
        """Close database session"""
        if self.session:
            self.session.close()

