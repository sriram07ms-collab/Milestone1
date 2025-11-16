"""Scraper for Groww ICICI Prudential AMC page"""
import logging
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag
from data_collection.base_scraper import BaseScraper
from data_collection.utils import (
    clean_text, validate_url, normalize_fund_name,
    extract_category_from_text, parse_risk_level, parse_exit_load,
    extract_number, extract_percentage
)
from config.settings import GROWW_ICICI_AMC_URL, GROWW_BASE_URL, TARGET_CATEGORIES

logger = logging.getLogger(__name__)


class GrowwAMCScraper(BaseScraper):
    """Scraper for ICICI Prudential AMC listing page"""
    
    def __init__(self):
        super().__init__()
        self.target_categories = TARGET_CATEGORIES
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape the main AMC page and extract fund information"""
        logger.info(f"Starting scrape of {GROWW_ICICI_AMC_URL}")
        
        soup = self.fetch_page(GROWW_ICICI_AMC_URL)
        if not soup:
            logger.error("Failed to fetch AMC page")
            return []
        
        funds = []
        
        # Find the table containing fund information
        # Try multiple selectors for the table
        table = None
        
        # First try standard table tag
        table = soup.find('table')
        
        # If not found, try div with table role or class
        if not table:
            table = soup.find('div', {'role': 'table'})
        
        if not table:
            # Try finding by class patterns
            table = soup.find('div', class_=re.compile(r'table|grid', re.I))
        
        if not table:
            # Try finding tbody
            tbody = soup.find('tbody')
            if tbody:
                table = tbody
        
        if not table:
            # Last resort: find all links to mutual funds
            logger.info("Table not found, trying to extract from fund links")
            fund_links = soup.find_all('a', href=re.compile(r'/mutual-funds/icici-prudential.*-direct-growth', re.I))
            if fund_links:
                for link in fund_links:
                    fund_name = clean_text(link.get_text())
                    fund_url = validate_url(link.get('href'), GROWW_BASE_URL)
                    if fund_name and fund_url:
                        # Extract category from parent or nearby elements
                        parent = link.find_parent(['tr', 'div', 'li'])
                        category = None
                        if parent:
                            category_text = parent.get_text()
                            category = extract_category_from_text(category_text)
                        
                        fund_data = {
                            'scheme_name': normalize_fund_name(fund_name),
                            'groww_url': fund_url,
                            'category': category or 'Unknown'
                        }
                        
                        # Filter for target categories
                        if any(target_cat.lower() in fund_data.get('category', '').lower() for target_cat in self.target_categories):
                            funds.append(fund_data)
                            logger.info(f"Extracted fund from link: {fund_data.get('scheme_name')}")
            
            logger.info(f"Extracted {len(funds)} funds from links")
            return funds
        
        # Extract rows from table
        rows = []
        if table.name == 'table':
            rows = table.find_all('tr')
        elif table.name == 'tbody':
            rows = table.find_all('tr')
        else:
            rows = table.find_all(['tr', 'div'], class_=re.compile(r'row|tr', re.I))
        
        if not rows:
            logger.warning("No rows found in table")
            return []
        
        # Skip header row (usually first row)
        start_idx = 1 if len(rows) > 1 else 0
        for row in rows[start_idx:]:
            try:
                fund_data = self._extract_fund_from_row(row)
                if fund_data:
                    # Filter for target categories (Large Cap, Mid Cap, Small Cap)
                    category = fund_data.get('category', '')
                    if any(target_cat.lower() in category.lower() for target_cat in self.target_categories):
                        funds.append(fund_data)
                        logger.info(f"Extracted fund: {fund_data.get('scheme_name')}")
            except Exception as e:
                logger.error(f"Error extracting fund from row: {e}")
                continue
        
        logger.info(f"Extracted {len(funds)} funds from AMC page")
        return funds
    
    def _extract_fund_from_row(self, row: Tag) -> Optional[Dict[str, Any]]:
        """Extract fund data from a table row"""
        cells = row.find_all(['td', 'th']) if row.name == 'tr' else row.find_all('div')
        
        if len(cells) < 3:
            return None
        
        fund_data = {}
        
        try:
            # Extract fund name and URL (usually in first cell)
            first_cell = cells[0]
            link = first_cell.find('a', href=True)
            
            if link:
                fund_name = clean_text(link.get_text())
                fund_url = validate_url(link.get('href'), GROWW_BASE_URL)
                
                if not fund_name or not fund_url:
                    return None
                
                fund_data['scheme_name'] = normalize_fund_name(fund_name)
                fund_data['groww_url'] = fund_url
            
            # Extract category (usually in second cell)
            if len(cells) > 1:
                category_text = clean_text(cells[1].get_text())
                fund_data['category'] = extract_category_from_text(category_text) or category_text
            
            # Extract risk level (usually in third cell)
            if len(cells) > 2:
                risk_text = clean_text(cells[2].get_text())
                fund_data['risk_level'] = parse_risk_level(risk_text)
            
            # Extract NAV (usually in fourth cell)
            if len(cells) > 3:
                nav_text = clean_text(cells[3].get_text())
                nav_value = extract_number(nav_text)
                if nav_value:
                    fund_data['nav'] = nav_value
            
            # Extract expense ratio (usually in fifth cell)
            if len(cells) > 4:
                expense_text = clean_text(cells[4].get_text())
                expense_ratio = extract_percentage(expense_text) or expense_text
                fund_data['expense_ratio'] = expense_ratio
            
            # Extract returns (1Y, 3Y, 5Y) - usually in cells 5, 6, 7
            if len(cells) > 5:
                returns_1y = extract_percentage(clean_text(cells[5].get_text()))
                fund_data['returns_1y'] = returns_1y
            
            if len(cells) > 6:
                returns_3y = extract_percentage(clean_text(cells[6].get_text()))
                fund_data['returns_3y'] = returns_3y
            
            if len(cells) > 7:
                returns_5y = extract_percentage(clean_text(cells[7].get_text()))
                fund_data['returns_5y'] = returns_5y
            
            # Extract rating (usually in cell 8)
            if len(cells) > 8:
                rating_text = clean_text(cells[8].get_text())
                rating = extract_number(rating_text)
                if rating:
                    fund_data['rating'] = int(rating)
            
            # Extract fund size (usually in cell 9)
            if len(cells) > 9:
                size_text = clean_text(cells[9].get_text())
                # Remove 'Cr' and extract number
                size_match = re.search(r'₹?\s*(\d+[\d,]*\.?\d*)\s*[Cc]r', size_text)
                if size_match:
                    size_str = size_match.group(1).replace(',', '')
                    try:
                        fund_data['fund_size_cr'] = float(size_str)
                    except ValueError:
                        pass
            
            # Extract exit load (usually in last cell)
            if len(cells) > 10:
                exit_load_text = clean_text(cells[-1].get_text())
                fund_data['exit_load'] = parse_exit_load(exit_load_text)
            
            # Validate that we have at least name and URL
            if not fund_data.get('scheme_name') or not fund_data.get('groww_url'):
                return None
            
            return fund_data
            
        except Exception as e:
            logger.error(f"Error parsing row: {e}")
            return None
    
    def get_all_fund_urls(self) -> List[str]:
        """Get all fund URLs from the AMC page"""
        funds = self.scrape()
        return [fund['groww_url'] for fund in funds if fund.get('groww_url')]

