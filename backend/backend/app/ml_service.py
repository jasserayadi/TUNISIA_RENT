# ============================================================
# app/ml_service.py
# ============================================================
import joblib
import pandas as pd
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "model.pkl"

FEATURES = [
    "surface", "bedrooms", "bathrooms",
    "is_house", "furnished", "parking", "elevator", "aircon",
    "heating", "security", "pool", "sea_view", "terrace",
    "equipped_kitchen", "governorate", "city",
]

BOOL_FEATURES = [
    "is_house", "furnished", "parking", "elevator", "aircon",
    "heating", "security", "pool", "sea_view", "terrace",
    "equipped_kitchen",
]

# Used only when ml/model.pkl is missing, so the API still works.
GOVERNORATE_FACTOR = {
    "tunis": 1.25, "ariana": 1.12, "ben arous": 1.05, "manouba": 0.95,
    "la marsa": 1.45, "gammarth": 1.60, "carthage": 1.50, "sidi bou said": 1.55,
    "nabeul": 0.95, "hammamet": 1.15, "sousse": 1.10, "monastir": 1.05,
    "mahdia": 0.90, "sfax": 0.95, "bizerte": 0.90, "beja": 0.80,
    "jendouba": 0.78, "kef": 0.78, "siliana": 0.75, "zaghouan": 0.80,
    "kairouan": 0.80, "kasserine": 0.75, "sidi bouzid": 0.75,
    "gabes": 0.85, "medenine": 0.90, "djerba": 1.25, "tataouine": 0.70,
    "gafsa": 0.78, "tozeur": 0.85, "kebili": 0.78,
}


class MLService:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.loaded = False
        self.model_name = "fallback-heuristic"
        self._load()

    # ---------------- loading ----------------
    def _load(self):
        try:
            saved = joblib.load(MODEL_PATH)
            self.model = saved["model"]
            self.preprocessor = saved["preprocessor"]
            self.model_name = saved.get("model_name", type(self.model).__name__)
            self.loaded = True
            print(f"✅ ML model loaded from {MODEL_PATH} ({self.model_name})")
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️  Could not load ML model ({exc}). Using fallback estimator.")

    # ---------------- helpers ----------------
    @staticmethod
    def _to_frame(payload: dict) -> pd.DataFrame:
        row = {
            "surface": float(payload["surface"]),
            "bedrooms": int(payload["bedrooms"]),
            "bathrooms": int(payload["bathrooms"]),
            "governorate": str(payload["governorate"]),
            "city": str(payload["city"]),
        }
        for feat in BOOL_FEATURES:
            row[feat] = int(bool(payload.get(feat, False)))
        return pd.DataFrame([row])[FEATURES]

    @staticmethod
    def _fallback(payload: dict) -> float:
        gov = str(payload.get("governorate", "")).strip().lower()
        factor = GOVERNORATE_FACTOR.get(gov, 1.0)

        price = 300 + float(payload["surface"]) * 6.5
        price += int(payload["bedrooms"]) * 90
        price += int(payload["bathrooms"]) * 60

        for feat, value in (
            ("furnished", 180), ("parking", 70), ("elevator", 60),
            ("aircon", 80), ("heating", 50), ("security", 90),
            ("pool", 250), ("sea_view", 250), ("terrace", 60),
            ("equipped_kitchen", 90), ("is_house", 150),
        ):
            if payload.get(feat):
                price += value

        return price * factor

    # ---------------- public API ----------------
    def predict(self, payload: dict) -> float:
        if self.loaded:
            frame = self._to_frame(payload)
            processed = self.preprocessor.transform(frame)
            return float(self.model.predict(processed)[0])
        return self._fallback(payload)


# singleton used by the routers
ml_service = MLService()
