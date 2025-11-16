"""Main orchestrator for scraping ICICI Prudential funds"""
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from data_collection.groww_amc_scraper import GrowwAMCScraper
from data_collection.groww_fund_scraper import GrowwFundScraper
from data_collection.utils import validate_fund_data, validate_url
from database.models import Scheme, SchemeFact, ScrapingLog, SessionLocal
from database.db_connection import get_db_session

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScraperOrchestrator:
    """Orchestrates the scraping process"""
    
    def __init__(self):
        self.amc_scraper = GrowwAMCScraper()
        self.fund_scraper = GrowwFundScraper()
        self.extraction_date = date.today()
    
    def scrape_all_funds(self) -> Dict[str, Any]:
        """Scrape all ICICI Prudential funds"""
        logger.info("Starting full scraping process")
        
        results = {
            'total_funds': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Step 1: Scrape AMC page to get fund list
            logger.info("Step 1: Scraping AMC page for fund list")
            funds_from_amc = self.amc_scraper.scrape()
            results['total_funds'] = len(funds_from_amc)
            
            if not funds_from_amc:
                logger.error("No funds found on AMC page")
                return results
            
            logger.info(f"Found {len(funds_from_amc)} funds on AMC page")
            
            # Step 2: Scrape each individual fund page
            logger.info("Step 2: Scraping individual fund pages")
            for fund_data in funds_from_amc:
                fund_url = fund_data.get('groww_url')
                if not fund_url:
                    results['failed'] += 1
                    results['errors'].append(f"Fund missing URL: {fund_data.get('scheme_name')}")
                    continue
                
                try:
                    # Scrape detailed fund page
                    detailed_data = self.fund_scraper.scrape(fund_url)
                    
                    if detailed_data:
                        # Merge data from AMC page and detailed page
                        merged_data = {**fund_data, **detailed_data}
                        merged_data['groww_url'] = fund_url  # Ensure URL is preserved
                        
                        # Validate data
                        is_valid, errors = validate_fund_data(merged_data)
                        if not is_valid:
                            logger.warning(f"Validation errors for {merged_data.get('scheme_name')}: {errors}")
                            results['errors'].extend([f"{merged_data.get('scheme_name')}: {err}" for err in errors])
                        
                        # Save to database
                        if self._save_fund_to_db(merged_data):
                            results['successful'] += 1
                            logger.info(f"Successfully saved: {merged_data.get('scheme_name')}")
                        else:
                            results['failed'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to scrape: {fund_url}")
                        
                except Exception as e:
                    logger.error(f"Error scraping {fund_url}: {e}")
                    results['failed'] += 1
                    results['errors'].append(f"{fund_url}: {str(e)}")
                    self._log_scraping_error(fund_url, str(e))
            
            logger.info(f"Scraping complete: {results['successful']} successful, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Fatal error in scraping process: {e}")
            results['errors'].append(f"Fatal error: {str(e)}")
            return results
    
    def _save_fund_to_db(self, fund_data: Dict[str, Any]) -> bool:
        """Save fund data to database"""
        try:
            with get_db_session() as session:
                # Check if scheme already exists
                scheme = session.query(Scheme).filter_by(groww_url=fund_data['groww_url']).first()
                
                if scheme:
                    # Update existing scheme
                    for key, value in fund_data.items():
                        if key not in ['groww_url', 'scheme_name'] and hasattr(scheme, key):
                            setattr(scheme, key, value)
                    scheme.updated_at = datetime.utcnow()
                else:
                    # Create new scheme
                    scheme = Scheme(
                        scheme_name=fund_data.get('scheme_name'),
                        scheme_slug=self._extract_slug_from_url(fund_data['groww_url']),
                        category=fund_data.get('category'),
                        risk_level=fund_data.get('risk_level'),
                        nav=fund_data.get('nav'),
                        expense_ratio=fund_data.get('expense_ratio'),
                        rating=fund_data.get('rating'),
                        fund_size_cr=fund_data.get('fund_size_cr'),
                        returns_1y=fund_data.get('returns_1y'),
                        returns_3y=fund_data.get('returns_3y'),
                        returns_5y=fund_data.get('returns_5y'),
                        groww_url=fund_data['groww_url']
                    )
                    session.add(scheme)
                    session.flush()  # Get scheme_id
                
                # Save facts
                fact_types = {
                    'expense_ratio': fund_data.get('expense_ratio'),
                    'exit_load': fund_data.get('exit_load'),
                    'min_lumpsum': fund_data.get('min_lumpsum'),
                    'min_sip': fund_data.get('min_sip'),
                    'lock_in_period': fund_data.get('lock_in_period'),
                    'riskometer': fund_data.get('risk_level'),
                    'benchmark': fund_data.get('benchmark'),
                    'statement_download': fund_data.get('statement_download_info'),
                }
                
                for fact_type, fact_value in fact_types.items():
                    if fact_value:
                        # Check if fact already exists for today
                        existing_fact = session.query(SchemeFact).filter_by(
                            scheme_id=scheme.scheme_id,
                            fact_type=fact_type,
                            extraction_date=self.extraction_date
                        ).first()
                        
                        if existing_fact:
                            # Update existing fact
                            existing_fact.fact_value = str(fact_value)
                            existing_fact.source_url = fund_data['groww_url']
                        else:
                            # Create new fact
                            fact = SchemeFact(
                                scheme_id=scheme.scheme_id,
                                fact_type=fact_type,
                                fact_value=str(fact_value),
                                source_url=fund_data['groww_url'],
                                extraction_date=self.extraction_date,
                                is_active=True
                            )
                            session.add(fact)
                
                # Log successful scraping
                self._log_scraping_success(fund_data['groww_url'], fund_data.get('scheme_name'), len(fact_types))
                
                return True
                
        except Exception as e:
            logger.error(f"Error saving fund to database: {e}")
            return False
    
    def _extract_slug_from_url(self, url: str) -> Optional[str]:
        """Extract slug from Groww URL"""
        try:
            parts = url.split('/')
            if 'mutual-funds' in parts:
                idx = parts.index('mutual-funds')
                if idx + 1 < len(parts):
                    return parts[idx + 1]
        except Exception:
            pass
        return None
    
    def _log_scraping_success(self, url: str, scheme_name: str, records_count: int):
        """Log successful scraping"""
        try:
            with get_db_session() as session:
                log = ScrapingLog(
                    source_url=url,
                    scheme_name=scheme_name,
                    status='success',
                    records_extracted=records_count
                )
                session.add(log)
        except Exception as e:
            logger.error(f"Error logging success: {e}")
    
    def _log_scraping_error(self, url: str, error_message: str):
        """Log scraping error"""
        try:
            with get_db_session() as session:
                log = ScrapingLog(
                    source_url=url,
                    status='failed',
                    error_message=error_message
                )
                session.add(log)
        except Exception as e:
            logger.error(f"Error logging error: {e}")

