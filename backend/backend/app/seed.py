# ============================================================
# app/seed.py  ->  run with:  python -m app.seed
# ============================================================
"""Insert synthetic demo data into the database.

⚠ The generated data is SYNTHETIC and must not be presented as
   real Tunisian market statistics.
"""
import random

from app.database import Base, SessionLocal, engine
from app.models import Property

random.seed(42)

LOCATIONS = [
    ("Tunis", "Tunis Centre", 1.25, 14),
    ("Tunis", "Bab Bhar", 1.15, 12),
    ("Tunis", "El Menzah", 1.30, 15),
    ("Ariana", "Ariana Ville", 1.12, 12),
    ("Ariana", "Raoued", 1.05, 11),
    ("Ariana", "Soukra", 1.08, 11),
    ("Ben Arous", "Ben Arous", 1.00, 10),
    ("Ben Arous", "Ezzahra", 1.02, 11),
    ("La Marsa", "La Marsa", 1.45, 18),
    ("La Marsa", "Gammarth", 1.60, 22),
    ("Carthage", "Carthage", 1.50, 19),
    ("Nabeul", "Hammamet", 1.15, 13),
    ("Nabeul", "Nabeul", 0.95, 10),
    ("Sousse", "Sousse Ville", 1.10, 12),
    ("Sousse", "Khezama", 1.12, 12),
    ("Monastir", "Monastir", 1.05, 11),
    ("Sfax", "Sfax Ville", 0.95, 9),
    ("Bizerte", "Bizerte", 0.90, 9),
    ("Medenine", "Djerba", 1.25, 15),
    ("Gabes", "Gabes", 0.85, 8),
]

CONDITIONS = ["excellent", "good", "average", "needs_work"]


def build_property() -> Property:
    governorate, city, factor, base_m2 = random.choice(LOCATIONS)

    surface = round(random.uniform(45, 180), 1)
    bedrooms = max(1, min(6, int(surface // 35) + random.choice([0, 0, 1])))
    bathrooms = max(1, min(4, bedrooms - random.choice([0, 1, 1])))
    floor = random.randint(0, 6)
    condition = random.choices(CONDITIONS, weights=[15, 50, 25, 10])[0]

    furnished = random.random() < 0.35
    parking = random.random() < 0.45
    elevator = random.random() < 0.55
    aircon = random.random() < 0.5
    heating = random.random() < 0.45
    security = random.random() < 0.3
    pool = random.random() < 0.07
    sea_view = random.random() < 0.12
    terrace = random.random() < 0.4
    equipped_kitchen = random.random() < 0.5
    is_house = random.random() < 0.2

    rent = surface * base_m2 * factor
    rent += bedrooms * 70
    rent += bathrooms * 45
    rent += 150 if furnished else 0
    rent += 60 if parking else 0
    rent += 50 if elevator else 0
    rent += 70 if aircon else 0
    rent += 40 if heating else 0
    rent += 80 if security else 0
    rent += 220 if pool else 0
    rent += 220 if sea_view else 0
    rent += 50 if terrace else 0
    rent += 80 if equipped_kitchen else 0
    rent += 120 if is_house else 0

    rent *= {"excellent": 1.12, "good": 1.0, "average": 0.9, "needs_work": 0.78}[condition]
    rent *= random.uniform(0.9, 1.12)

    return Property(
        governorate=governorate,
        city=city,
        surface=surface,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        floor=floor,
        condition=condition,
        is_house=is_house,
        furnished=furnished,
        parking=parking,
        elevator=elevator,
        aircon=aircon,
        heating=heating,
        security=security,
        pool=pool,
        sea_view=sea_view,
        terrace=terrace,
        equipped_kitchen=equipped_kitchen,
        rent=round(rent, -1),
    )


def main(count: int = 250):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Property).count() > 0:
            print("ℹ️  Database already contains properties — skipping seed.")
            return
        db.add_all([build_property() for _ in range(count)])
        db.commit()
        print(f"✅ Inserted {count} synthetic demo properties.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
