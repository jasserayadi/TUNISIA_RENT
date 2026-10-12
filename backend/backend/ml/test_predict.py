"""
Test Surface & Bedrooms with Monotonic Constraints model
"""

import joblib
import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
saved = joblib.load(SCRIPT_DIR / "model.pkl")

model = saved["model"]
preprocessor = saved["preprocessor"]

print("Model loaded successfully!\n")

def predict(example: dict, title: str):
    df = pd.DataFrame([example])
    X_processed = preprocessor.transform(df)
    pred = model.predict(X_processed)[0]
    print("=" * 55)
    print(title)
    print(f"→ Estimated rent : {pred:.0f} TND")
    return pred


base = {
    "surface": 90,
    "bedrooms": 2,
    "bathrooms": 1,
    "is_house": 0,
    "furnished": 0,
    "parking": 1,
    "elevator": 0,
    "aircon": 0,
    "heating": 0,
    "security": 0,
    "pool": 0,
    "sea_view": 0,
    "terrace": 0,
    "equipped_kitchen": 0,
    "governorate": "Ariana",
    "city": "Ariana Ville"
}

print("▶ EFFECT OF SURFACE (bedrooms fixed at 2)")
print("-" * 55)

s70  = base.copy(); s70["surface"] = 70
s90  = base.copy(); s90["surface"] = 90
s120 = base.copy(); s120["surface"] = 120
s150 = base.copy(); s150["surface"] = 150

p70  = predict(s70,  "70 m²  | 2 bedrooms")
p90  = predict(s90,  "90 m²  | 2 bedrooms")
p120 = predict(s120, "120 m² | 2 bedrooms")
p150 = predict(s150, "150 m² | 2 bedrooms")

print("\n▶ EFFECT OF BEDROOMS (surface fixed at 100 m²)")
print("-" * 55)

b1 = base.copy(); b1.update({"surface": 100, "bedrooms": 1})
b2 = base.copy(); b2.update({"surface": 100, "bedrooms": 2})
b3 = base.copy(); b3.update({"surface": 100, "bedrooms": 3})
b4 = base.copy(); b4.update({"surface": 100, "bedrooms": 4})

p1 = predict(b1, "100 m² | 1 bedroom")
p2 = predict(b2, "100 m² | 2 bedrooms")
p3 = predict(b3, "100 m² | 3 bedrooms")
p4 = predict(b4, "100 m² | 4 bedrooms")

print("\n" + "=" * 55)
print("SUMMARY")
print("=" * 55)
print(f"Surface 70 → 90 → 120 → 150 m²")
print(f"{p70:.0f} → {p90:.0f} → {p120:.0f} → {p150:.0f} TND")
print()
print(f"Bedrooms 1 → 2 → 3 → 4")
print(f"{p1:.0f} → {p2:.0f} → {p3:.0f} → {p4:.0f} TND")