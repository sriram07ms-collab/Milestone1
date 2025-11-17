"""
Export current database contents to data/seed_data.json
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from database.models import Scheme, SchemeFact, SessionLocal


def export_seed_data():
    session = SessionLocal()

    try:
        schemes = session.query(Scheme).all()
        facts = session.query(SchemeFact).all()

        seed_data = {
            "schemes": [],
            "facts": []
        }

        for scheme in schemes:
            seed_data["schemes"].append({
                "scheme_slug": scheme.scheme_slug,
                "scheme_name": scheme.scheme_name,
                "category": scheme.category,
                "risk_level": scheme.risk_level,
                "nav": scheme.nav,
                "expense_ratio": scheme.expense_ratio,
                "rating": scheme.rating,
                "fund_size_cr": scheme.fund_size_cr,
                "returns_1y": scheme.returns_1y,
                "returns_3y": scheme.returns_3y,
                "returns_5y": scheme.returns_5y,
                "groww_url": scheme.groww_url
            })

        scheme_lookup = {s.scheme_id: s.scheme_slug for s in schemes}

        for fact in facts:
            scheme_slug = scheme_lookup.get(fact.scheme_id)
            if not scheme_slug:
                continue

            seed_data["facts"].append({
                "scheme_slug": scheme_slug,
                "fact_type": fact.fact_type,
                "fact_value": fact.fact_value,
                "source_url": fact.source_url,
                "extraction_date": fact.extraction_date.isoformat() if fact.extraction_date else None
            })

        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        output_path = data_dir / "seed_data.json"

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(seed_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Seed data exported to {output_path}")

    finally:
        session.close()


if __name__ == "__main__":
    export_seed_data()

