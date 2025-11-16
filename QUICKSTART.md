# Quick Start Guide

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Initialize the database:**
The database will be automatically created when you run the scraper for the first time.

## Testing the Scraper

### Test with a Single Fund Page

Test the scraper with the example URL:
```bash
python test_scraper.py
```

This will:
- Scrape the ICICI Prudential Large & Mid Cap Fund page
- Extract all available data
- Validate the extracted data
- Display results

### Run Full Scraping

Scrape all ICICI Prudential Large/Mid/Small Cap funds:
```bash
python main.py
```

This will:
1. Scrape the main AMC page to get all fund links
2. Filter for Large Cap, Mid Cap, and Small Cap funds
3. Scrape each individual fund page
4. Extract all required data fields
5. Validate data and URLs
6. Store in database with source URLs

## Expected Output

### From Test Scraper

You should see output like:
```
scheme_name: ICICI Prudential Large & Mid Cap Fund
groww_url: https://groww.in/mutual-funds/icici-prudential-top-100-fund-direct-growth
category: Large & MidCap
risk_level: Very High
nav: 1179.13
expense_ratio: 0.77%
rating: 5
fund_size_cr: 25752.59
min_sip: ₹100
min_lumpsum: ₹5,000
exit_load: Exit load of 1% if redeemed within 1 month
benchmark: NIFTY Large Midcap 250 Total Return Index
```

### From Main Scraper

You should see:
```
Scraping Results Summary
Total funds found: X
Successfully scraped: X
Failed: 0
```

## Data Validation

The scraper validates:
- ✅ All URLs are valid Groww URLs
- ✅ Required fields (scheme_name, groww_url) are present
- ✅ Data formats are correct
- ✅ No invalid URLs are stored

## Database

Data is stored in SQLite by default (`icici_funds.db`).

### Tables:
- `icici_schemes` - Basic scheme information
- `scheme_facts` - Individual facts with source URLs
- `scraping_logs` - Scraping operation logs

## Troubleshooting

### If scraping fails:
1. Check your internet connection
2. Verify Groww website is accessible
3. Check logs in `logs/scraper.log`
4. Ensure all dependencies are installed

### If data is missing:
- Some fields may not be available on all fund pages
- Check the scraping logs for specific errors
- The scraper will continue even if some fields are missing

## Next Steps

After successful data extraction:
1. Verify data in database
2. Proceed to chatbot implementation
3. Set up scheduled updates

