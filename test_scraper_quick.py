"""Quick test to verify scraper functionality"""
import sys
from database.models import Scheme, SchemeFact, SessionLocal

def check_database():
    """Check if database has data"""
    print("=" * 60)
    print("Database Status Check")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        scheme_count = db.query(Scheme).count()
        fact_count = db.query(SchemeFact).count()
        
        print(f"[OK] Schemes in database: {scheme_count}")
        print(f"[OK] Facts in database: {fact_count}")
        
        if scheme_count > 0:
            print("\nSample schemes:")
            schemes = db.query(Scheme).limit(3).all()
            for scheme in schemes:
                print(f"  - {scheme.scheme_name}")
                print(f"    URL: {scheme.groww_url}")
                print(f"    Category: {scheme.category}")
        
        if fact_count > 0:
            print("\nSample facts:")
            facts = db.query(SchemeFact).limit(3).all()
            for fact in facts:
                scheme = db.query(Scheme).filter_by(scheme_id=fact.scheme_id).first()
                print(f"  - {fact.fact_type}: {fact.fact_value}")
                print(f"    Scheme: {scheme.scheme_name if scheme else 'Unknown'}")
        
        print("\n" + "=" * 60)
        if scheme_count > 0 and fact_count > 0:
            print("[OK] Database has data - Scraper has been run successfully!")
            return True
        else:
            print("[FAIL] Database is empty - Scraper needs to be run")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error checking database: {e}")
        return False
    finally:
        db.close()

def test_scraper_imports():
    """Test if scraper modules can be imported"""
    print("\n" + "=" * 60)
    print("Scraper Module Import Test")
    print("=" * 60)
    
    try:
        from data_collection.groww_amc_scraper import GrowwAMCScraper
        print("[OK] GrowwAMCScraper imported successfully")
        
        from data_collection.groww_fund_scraper import GrowwFundScraper
        print("[OK] GrowwFundScraper imported successfully")
        
        from data_collection.scraper_orchestrator import ScraperOrchestrator
        print("[OK] ScraperOrchestrator imported successfully")
        
        print("\n[OK] All scraper modules can be imported!")
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SCRAPER STATUS CHECK")
    print("=" * 60 + "\n")
    
    imports_ok = test_scraper_imports()
    db_ok = check_database()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Scraper modules: {'[OK] Working' if imports_ok else '[FAIL] Error'}")
    print(f"Database data: {'[OK] Has data' if db_ok else '[FAIL] Empty'}")
    
    if imports_ok and db_ok:
        print("\n[SUCCESS] Scraper system is working as expected!")
        sys.exit(0)
    else:
        print("\n[ERROR] Some issues detected. Check errors above.")
        sys.exit(1)

