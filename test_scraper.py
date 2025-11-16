"""Test script for the scraper"""
import logging
from data_collection.groww_fund_scraper import GrowwFundScraper
from data_collection.utils import validate_fund_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_fund_scraper():
    """Test the fund scraper with the example URL"""
    test_url = "https://groww.in/mutual-funds/icici-prudential-top-100-fund-direct-growth"
    
    logger.info(f"Testing scraper with URL: {test_url}")
    
    scraper = GrowwFundScraper()
    fund_data = scraper.scrape(test_url)
    
    if fund_data:
        logger.info("=" * 80)
        logger.info("Scraped Data:")
        logger.info("=" * 80)
        
        # Print all extracted data
        for key, value in fund_data.items():
            logger.info(f"{key}: {value}")
        
        # Validate data
        is_valid, errors = validate_fund_data(fund_data)
        
        logger.info("=" * 80)
        logger.info("Validation Results:")
        logger.info("=" * 80)
        logger.info(f"Valid: {is_valid}")
        
        if errors:
            logger.warning("Validation Errors:")
            for error in errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("No validation errors!")
        
        # Check for expected fields
        expected_fields = [
            'scheme_name', 'groww_url', 'category', 'risk_level',
            'nav', 'expense_ratio', 'rating', 'fund_size_cr',
            'min_sip', 'min_lumpsum', 'exit_load'
        ]
        
        logger.info("=" * 80)
        logger.info("Field Coverage:")
        logger.info("=" * 80)
        for field in expected_fields:
            status = "✓" if fund_data.get(field) else "✗"
            logger.info(f"{status} {field}: {fund_data.get(field, 'Not found')}")
        
        return fund_data
    else:
        logger.error("Failed to scrape fund data")
        return None


if __name__ == "__main__":
    test_fund_scraper()

