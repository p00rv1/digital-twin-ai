from app.database.db import SessionLocal
from app.database.models import Biomarker

db = SessionLocal()

biomarkers = [
  ("tbil", "liver"),
    ("dbil", "liver"),
    ("alp", "liver"),
    ("alt", "liver"),
    ("ast", "liver"),
    ("total_proteins", "liver"),
    ("albumin", "liver"),
    ("ag_ratio", "liver")
]

for name, category in biomarkers:

    existing = (
        db.query(Biomarker)
        .filter(Biomarker.name == name)
        .first()
    )

    if not existing:
        db.add(
            Biomarker(
                name=name,
                category=category
            )
        )

db.commit()
db.close()

print("done")