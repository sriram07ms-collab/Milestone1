"""Base scraper class"""
import time
import logging
import requests
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from config.settings import REQUEST_DELAY, REQUEST_TIMEOUT, MAX_RETRIES, USER_AGENT

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def fetch_page(self, url: str, retries: int = MAX_RETRIES) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching URL (attempt {attempt + 1}/{retries}): {url}")
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                # Add delay between requests
                time.sleep(REQUEST_DELAY)
                
                soup = BeautifulSoup(response.content, 'lxml')
                return soup
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error fetching {url} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(REQUEST_DELAY * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
        
        return None
    
    @abstractmethod
    def scrape(self, *args, **kwargs) -> Dict[str, Any]:
        """Main scraping method - to be implemented by subclasses"""
        pass

