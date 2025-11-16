"""Utility functions for data collection"""
import re
import logging
import validators
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


def clean_text(text: Optional[str]) -> Optional[str]:
    """Clean and normalize text"""
    if not text:
        return None
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    return text if text else None


def extract_number(text: Optional[str]) -> Optional[float]:
    """Extract number from text"""
    if not text:
        return None
    # Remove currency symbols, commas, and extract number
    cleaned = re.sub(r'[₹,\s]', '', str(text))
    match = re.search(r'(\d+\.?\d*)', cleaned)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def extract_percentage(text: Optional[str]) -> Optional[str]:
    """Extract percentage value from text"""
    if not text:
        return None
    # Look for percentage pattern
    match = re.search(r'(\d+\.?\d*)\s*%', str(text))
    if match:
        return f"{match.group(1)}%"
    return None


def validate_url(url: Optional[str], base_url: str = "https://groww.in") -> Optional[str]:
    """Validate and normalize URL"""
    if not url:
        return None
    
    # Clean URL
    url = url.strip()
    
    # Handle relative URLs
    if url.startswith('/'):
        url = urljoin(base_url, url)
    elif not url.startswith('http'):
        url = urljoin(base_url, '/' + url)
    
    # Validate URL format
    if validators.url(url):
        # Ensure it's a Groww URL
        parsed = urlparse(url)
        if 'groww.in' in parsed.netloc:
            return url
    
    logger.warning(f"Invalid URL: {url}")
    return None


def normalize_fund_name(name: Optional[str]) -> Optional[str]:
    """Normalize fund name"""
    if not name:
        return None
    
    # Remove common suffixes
    name = re.sub(r'\s*Direct\s*Plan\s*Growth\s*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*Direct\s*Growth\s*$', '', name, flags=re.IGNORECASE)
    name = clean_text(name)
    return name


def extract_category_from_text(text: Optional[str]) -> Optional[str]:
    """Extract fund category from text"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Map common category terms
    category_map = {
        'large cap': 'Large Cap',
        'mid cap': 'Mid Cap',
        'small cap': 'Small Cap',
        'large & midcap': 'Large & MidCap',
        'large and midcap': 'Large & MidCap',
        'large & mid cap': 'Large & MidCap',
        'flexi cap': 'Flexi Cap',
        'multi cap': 'Multi Cap',
        'elss': 'ELSS',
        'equity': 'Equity',
        'debt': 'Debt',
        'hybrid': 'Hybrid'
    }
    
    for key, value in category_map.items():
        if key in text_lower:
            return value
    
    return None


def parse_exit_load(text: Optional[str]) -> Optional[str]:
    """Parse exit load information"""
    if not text:
        return None
    
    text = clean_text(text)
    
    # Handle "No exit load" or "-"
    if text in ['-', 'No exit load', 'N/A', 'NA']:
        return "No exit load"
    
    # Return as is if it contains exit load information
    if 'exit load' in text.lower() or '%' in text:
        return text
    
    return None


def parse_risk_level(text: Optional[str]) -> Optional[str]:
    """Parse risk level from text"""
    if not text:
        return None
    
    text = clean_text(text)
    text_lower = text.lower()
    
    risk_map = {
        'very high': 'Very High',
        'moderately high': 'Moderately High',
        'moderate': 'Moderate',
        'low to moderate': 'Low to Moderate',
        'low': 'Low'
    }
    
    for key, value in risk_map.items():
        if key in text_lower:
            return value
    
    return text  # Return original if no match


def validate_fund_data(data: Dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate extracted fund data"""
    errors = []
    
    # Required fields
    required_fields = ['scheme_name', 'groww_url']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Validate URL
    if data.get('groww_url'):
        validated_url = validate_url(data['groww_url'])
        if not validated_url:
            errors.append(f"Invalid URL: {data['groww_url']}")
        else:
            data['groww_url'] = validated_url
    
    # Validate numeric fields
    if data.get('expense_ratio'):
        if not re.match(r'^\d+\.?\d*%?$', str(data['expense_ratio']).replace('%', '')):
            errors.append(f"Invalid expense ratio format: {data['expense_ratio']}")
    
    if data.get('rating'):
        rating = data['rating']
        if isinstance(rating, (int, float)):
            if not (1 <= rating <= 5):
                errors.append(f"Rating must be between 1-5: {rating}")
    
    return len(errors) == 0, errors

