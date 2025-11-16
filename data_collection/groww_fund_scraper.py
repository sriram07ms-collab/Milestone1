"""Scraper for individual Groww fund pages"""
import logging
import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup, Tag
from data_collection.base_scraper import BaseScraper
from data_collection.utils import (
    clean_text, validate_url, extract_number, extract_percentage,
    parse_exit_load, parse_risk_level, extract_category_from_text
)

logger = logging.getLogger(__name__)


class GrowwFundScraper(BaseScraper):
    """Scraper for individual fund detail pages"""
    
    def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape an individual fund page"""
        logger.info(f"Scraping fund page: {url}")
        
        soup = self.fetch_page(url)
        if not soup:
            logger.error(f"Failed to fetch fund page: {url}")
            return None
        
        fund_data = {'groww_url': validate_url(url)}
        
        try:
            # Extract fund name from page title or header
            fund_data.update(self._extract_fund_name(soup))
            
            # Extract basic information
            fund_data.update(self._extract_basic_info(soup))
            
            # Extract minimum investment amounts
            fund_data.update(self._extract_minimum_investments(soup))
            
            # Extract exit load
            fund_data.update(self._extract_exit_load(soup))
            
            # Extract lock-in period (for ELSS)
            fund_data.update(self._extract_lock_in_period(soup))
            
            # Extract benchmark
            fund_data.update(self._extract_benchmark(soup))
            
            # Extract riskometer
            fund_data.update(self._extract_riskometer(soup))
            
            # Extract statement download instructions
            fund_data.update(self._extract_statement_download_info(soup))
            
            # Extract additional details from the page
            fund_data.update(self._extract_additional_info(soup))
            
            logger.info(f"Successfully scraped fund: {fund_data.get('scheme_name')}")
            return fund_data
            
        except Exception as e:
            logger.error(f"Error scraping fund page {url}: {e}")
            return None
    
    def _extract_fund_name(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract fund name from page"""
        data = {}
        
        # Try multiple selectors for fund name
        selectors = [
            'h1',
            ('div', {'class': re.compile(r'fund.*name|title', re.I)}),
            ('span', {'class': re.compile(r'fund.*name', re.I)}),
        ]
        
        for selector in selectors:
            if isinstance(selector, tuple):
                tag, attrs = selector
                element = soup.find(tag, attrs)
            else:
                element = soup.find(selector)
            
            if element:
                name = clean_text(element.get_text())
                if name and len(name) > 5:  # Reasonable name length
                    data['scheme_name'] = name
                    break
        
        return data
    
    def _extract_basic_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract basic fund information"""
        data = {}
        text = soup.get_text()
        
        # Extract NAV - Look for "NAV: 14 Nov 2025 ₹1,179.13" pattern
        nav_patterns = [
            r'NAV[:\s]*\d+\s+\w+\s+\d+\s*₹\s*(\d+[\d,]*\.?\d*)',  # NAV: date ₹amount
            r'NAV[:\s]*₹?\s*(\d+[\d,]*\.?\d*)',  # NAV: ₹amount
            r'₹\s*(\d+[\d,]*\.?\d*)',  # Just ₹amount
        ]
        
        for pattern in nav_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                nav_str = match.group(1).replace(',', '')
                try:
                    data['nav'] = float(nav_str)
                    break
                except ValueError:
                    continue
        
        # Extract expense ratio
        expense_patterns = [
            r'Expense\s+Ratio[:\s]*(\d+\.?\d*)\s*%?',
            r'(\d+\.?\d*)\s*%\s*Expense',
        ]
        
        for pattern in expense_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['expense_ratio'] = f"{match.group(1)}%"
                break
        
        # Extract rating - Look for "Rating 5" pattern
        rating_patterns = [
            r'Rating\s*(\d+)',
            r'(\d+)\s*Rating',
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    rating = int(match.group(1))
                    if 1 <= rating <= 5:
                        data['rating'] = rating
                        break
                except ValueError:
                    continue
        
        # Extract fund size - Look for "Fund size ₹25,752.59Cr" pattern
        size_patterns = [
            r'Fund\s+size[:\s]*₹\s*(\d+[\d,]*\.?\d*)\s*[Cc]r',
            r'₹\s*(\d+[\d,]*\.?\d*)\s*[Cc]r',
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                size_str = match.group(1).replace(',', '')
                try:
                    data['fund_size_cr'] = float(size_str)
                    break
                except ValueError:
                    continue
        
        # Extract category
        category_elem = soup.find(string=re.compile(r'Category|Type', re.I))
        if category_elem:
            parent = category_elem.find_parent()
            if parent:
                category_text = parent.get_text()
                data['category'] = extract_category_from_text(category_text)
        
        # Extract risk level
        risk_elem = soup.find(string=re.compile(r'Risk', re.I))
        if risk_elem:
            parent = risk_elem.find_parent()
            if parent:
                risk_text = parent.get_text()
                data['risk_level'] = parse_risk_level(risk_text)
        
        # Extract returns - Look for "3Y annualised +22.44%" pattern
        returns_patterns = [
            (r'1[Yy]\s+[:\s]*([+-]?\d+\.?\d*)\s*%', 'returns_1y'),
            (r'3[Yy]\s+annualised\s*([+-]?\d+\.?\d*)\s*%', 'returns_3y'),
            (r'3[Yy]\s+[:\s]*([+-]?\d+\.?\d*)\s*%', 'returns_3y'),
            (r'5[Yy]\s+[:\s]*([+-]?\d+\.?\d*)\s*%', 'returns_5y'),
        ]
        
        for pattern, key in returns_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and key not in data:
                data[key] = f"{match.group(1)}%"
        
        return data
    
    def _extract_minimum_investments(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract minimum investment amounts"""
        data = {}
        text = soup.get_text()
        
        # Extract minimum SIP - Look for "Min. SIP amount ₹100" pattern
        sip_patterns = [
            r'Min\.?\s*SIP\s*amount[:\s]*₹\s*(\d+[\d,]*)',
            r'Min\.?\s*SIP[:\s]*₹\s*(\d+[\d,]*)',
            r'SIP[:\s]*₹\s*(\d+[\d,]*)',
            r'Minimum\s+SIP[:\s]*₹\s*(\d+[\d,]*)',
        ]
        
        for pattern in sip_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sip_str = match.group(1).replace(',', '')
                data['min_sip'] = f"₹{sip_str}"
                break
        
        # Extract minimum lumpsum - Look for "Minimum Lumpsum Investment is ₹5,000" pattern
        lumpsum_patterns = [
            r'Minimum\s+Lumpsum\s+Investment\s+is\s*₹\s*(\d+[\d,]*)',
            r'Min\.?\s*Lumpsum[:\s]*₹\s*(\d+[\d,]*)',
            r'Minimum\s+Lumpsum[:\s]*₹\s*(\d+[\d,]*)',
            r'Lump\s+sum\s+minimum[:\s]*₹\s*(\d+[\d,]*)',
        ]
        
        for pattern in lumpsum_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                lumpsum_str = match.group(1).replace(',', '')
                data['min_lumpsum'] = f"₹{lumpsum_str}"
                break
        
        return data
    
    def _extract_exit_load(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract exit load information"""
        data = {}
        text = soup.get_text()
        
        # Look for "Exit load of 1% if redeemed within 1 month" pattern
        exit_load_patterns = [
            r'Exit\s+load\s+of\s+(\d+\.?\d*)\s*%\s+if\s+redeemed\s+within\s+(\d+)\s*(day|month|year)',
            r'Exit\s+load\s+of\s+(\d+\.?\d*)\s*%\s+if\s+redeemed\s+within\s+(\d+)\s*(days|months|years)',
            r'Exit\s+load[:\s]*(\d+\.?\d*)\s*%',
        ]
        
        for pattern in exit_load_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    period_type = match.group(3) if len(match.groups()) > 2 else 'days'
                    data['exit_load'] = f"Exit load of {match.group(1)}% if redeemed within {match.group(2)} {period_type}"
                else:
                    data['exit_load'] = f"Exit load of {match.group(1)}%"
                break
        
        if not data.get('exit_load'):
            # Check for "No exit load" or "-"
            if re.search(r'no\s+exit\s+load|exit\s+load[:\s]*-', text, re.IGNORECASE):
                data['exit_load'] = "No exit load"
        
        return data
    
    def _extract_lock_in_period(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract lock-in period (for ELSS schemes)"""
        data = {}
        text = soup.get_text()
        
        # Check if it's an ELSS scheme
        is_elss = bool(re.search(r'ELSS|Tax\s+Saver', text, re.IGNORECASE))
        
        if is_elss:
            # ELSS typically has 3 years lock-in
            lock_in_match = re.search(r'lock[-\s]*in[:\s]*(\d+)\s*(year|month)', text, re.IGNORECASE)
            if lock_in_match:
                data['lock_in_period'] = f"{lock_in_match.group(1)} {lock_in_match.group(2)}s"
            else:
                # Default for ELSS
                data['lock_in_period'] = "3 years"
        else:
            data['lock_in_period'] = "No lock-in"
        
        return data
    
    def _extract_benchmark(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract benchmark information"""
        data = {}
        text = soup.get_text()
        
        # Look for "Fund benchmark | NIFTY Large Midcap 250 Total Return Index" pattern
        benchmark_patterns = [
            r'Fund\s+benchmark\s*\|?\s*([^\n|]+)',
            r'Fund\s+benchmark[:\s]*([^\n]+)',
            r'Benchmark[:\s]*([^\n]+)',
        ]
        
        for pattern in benchmark_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                benchmark = clean_text(match.group(1))
                if benchmark and len(benchmark) < 200:  # Reasonable length
                    # Clean up the benchmark text
                    benchmark = benchmark.strip('|').strip()
                    data['benchmark'] = benchmark
                    break
        
        return data
    
    def _extract_riskometer(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract riskometer details"""
        data = {}
        
        # Risk level is already extracted in basic info
        # This can be enhanced to extract more detailed riskometer info
        # For now, we use the risk level from basic info
        
        return data
    
    def _extract_statement_download_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract statement download instructions"""
        data = {}
        
        # Look for statement download links or instructions
        statement_keywords = ['statement', 'download', 'account statement', 'consolidated account statement']
        
        text = soup.get_text()
        for keyword in statement_keywords:
            if keyword.lower() in text.lower():
                # Try to find nearby text with instructions
                # This is a simplified version - can be enhanced
                data['statement_download_info'] = "Please visit your Groww account to download statements. You can find statements in the 'My Investments' section."
                break
        
        return data
    
    def _extract_additional_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract any additional scheme-specific information"""
        data = {}
        
        # Extract fund manager, launch date, etc. if available
        text = soup.get_text()
        
        # Fund manager
        manager_match = re.search(r'Fund\s+Manager[:\s]*([^\n]+)', text, re.IGNORECASE)
        if manager_match:
            data['fund_manager'] = clean_text(manager_match.group(1))
        
        # Launch date
        launch_match = re.search(r'Launch\s+Date[:\s]*([^\n]+)', text, re.IGNORECASE)
        if launch_match:
            data['launch_date'] = clean_text(launch_match.group(1))
        
        return data

