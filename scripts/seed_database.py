"""
Seed the database with default data when empty.
"""
import json
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from database.models import Scheme, SchemeFact, SessionLocal


def seed_database_from_file(seed_file: str = "data/seed_data.json") -> bool:
    """
    Seed the database with data from seed_file if no schemes exist.

    Returns:
        bool: True if seeding occurred, False otherwise.
    """
    seed_path = Path(seed_file)
    if not seed_path.exists():
        print(f"[INFO] Seed file not found: {seed_path}")
        return False

    session = SessionLocal()
    try:
        scheme_count = session.query(Scheme).count()
        if scheme_count > 0:
            print("[INFO] Database already has data. Skipping seed.")
            return False

        with seed_path.open("r", encoding="utf-8") as f:
            seed_data = json.load(f)

        slug_to_scheme = {}
        schemes = seed_data.get("schemes", [])
        for scheme_data in schemes:
            scheme = Scheme(
                scheme_name=scheme_data.get("scheme_name"),
                scheme_slug=scheme_data.get("scheme_slug"),
                category=scheme_data.get("category"),
                risk_level=scheme_data.get("risk_level"),
                nav=scheme_data.get("nav"),
                expense_ratio=scheme_data.get("expense_ratio"),
                rating=scheme_data.get("rating"),
                fund_size_cr=scheme_data.get("fund_size_cr"),
                returns_1y=scheme_data.get("returns_1y"),
                returns_3y=scheme_data.get("returns_3y"),
                returns_5y=scheme_data.get("returns_5y"),
                groww_url=scheme_data.get("groww_url")
            )
            session.add(scheme)
            session.flush()  # assign scheme_id
            slug_to_scheme[scheme.scheme_slug] = scheme

        facts = seed_data.get("facts", [])
        for fact_data in facts:
            slug = fact_data.get("scheme_slug")
            scheme = slug_to_scheme.get(slug)
            if not scheme:
                continue

            extraction_date = fact_data.get("extraction_date")
            extraction_date = date.fromisoformat(extraction_date) if extraction_date else None

            fact = SchemeFact(
                scheme_id=scheme.scheme_id,
                fact_type=fact_data.get("fact_type"),
                fact_value=fact_data.get("fact_value"),
                source_url=fact_data.get("source_url"),
                extraction_date=extraction_date,
                is_active=True
            )
            session.add(fact)

        session.commit()
        print("[OK] Database seeded successfully from seed_data.json")
        return True

    except Exception as exc:
        session.rollback()
        print(f"[ERROR] Failed to seed database: {exc}")
        return False
    finally:
        session.close()


if __name__ == "__main__":
    seed_database_from_file()

