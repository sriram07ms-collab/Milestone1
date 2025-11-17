"""Verify database and scripts are working"""
import sys

def test_database():
    """Test database modules"""
    print("=" * 60)
    print("Database Module Test")
    print("=" * 60)
    
    try:
        from database.models import Scheme, SchemeFact, init_db, SessionLocal
        print("[OK] Database models imported successfully")
        
        from database.db_connection import get_db_session
        print("[OK] Database connection module imported successfully")
        
        # Test database initialization
        init_db()
        print("[OK] Database initialization works")
        
        # Test database connection
        db = SessionLocal()
        scheme_count = db.query(Scheme).count()
        fact_count = db.query(SchemeFact).count()
        db.close()
        
        print(f"[OK] Database connection works - {scheme_count} schemes, {fact_count} facts")
        return True
    except Exception as e:
        print(f"[FAIL] Database test error: {e}")
        return False

def test_scripts():
    """Test scripts modules"""
    print("\n" + "=" * 60)
    print("Scripts Module Test")
    print("=" * 60)
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("generate_embeddings", "scripts/generate_embeddings.py")
        if spec and spec.loader:
            print("[OK] generate_embeddings.py can be loaded")
        else:
            print("[FAIL] generate_embeddings.py not found")
            return False
        
        # Try to import the module
        from scripts.generate_embeddings import generate_document_text
        print("[OK] Scripts module imports successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Scripts test error: {e}")
        return False

def check_git_status():
    """Check if files are tracked in git"""
    print("\n" + "=" * 60)
    print("Git Status Check")
    print("=" * 60)
    
    import subprocess
    
    try:
        # Check database files
        result = subprocess.run(['git', 'ls-files', 'database/'], 
                              capture_output=True, text=True)
        db_files = [f for f in result.stdout.strip().split('\n') if f]
        print(f"[OK] Database files tracked: {len(db_files)}")
        for f in db_files:
            print(f"  - {f}")
        
        # Check scripts files
        result = subprocess.run(['git', 'ls-files', 'scripts/'], 
                              capture_output=True, text=True)
        script_files = [f for f in result.stdout.strip().split('\n') if f]
        print(f"\n[OK] Script files tracked: {len(script_files)}")
        for f in script_files:
            print(f"  - {f}")
        
        return len(db_files) >= 3 and len(script_files) >= 2
    except Exception as e:
        print(f"[FAIL] Git check error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DATABASE & SCRIPTS VERIFICATION")
    print("=" * 60 + "\n")
    
    db_ok = test_database()
    scripts_ok = test_scripts()
    git_ok = check_git_status()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Database: {'[OK] Working' if db_ok else '[FAIL] Error'}")
    print(f"Scripts: {'[OK] Working' if scripts_ok else '[FAIL] Error'}")
    print(f"Git tracking: {'[OK] All files tracked' if git_ok else '[FAIL] Missing files'}")
    
    if db_ok and scripts_ok and git_ok:
        print("\n[SUCCESS] All database and scripts are committed and working!")
        sys.exit(0)
    else:
        print("\n[ERROR] Some issues detected. Check errors above.")
        sys.exit(1)

