"""
TounesRent - XGBoost with Monotonic Constraints
Forces: surface ↑ and bedrooms ↑ → rent ↑
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
import joblib
import json

SCRIPT_DIR = Path(__file__).resolve().parent

# -------------------------------------------------
# 1. Load data
# -------------------------------------------------
df = pd.read_csv(SCRIPT_DIR / "data" / "tunisian_rentals_final.csv")
print("=" * 60)
print("1. DATA LOADED")
print("=" * 60)
print("Shape:", df.shape)

# -------------------------------------------------
# 2. Features
# -------------------------------------------------
numeric_features = [
    "surface", "bedrooms", "bathrooms", "is_house",
    "furnished", "parking", "elevator", "aircon",
    "heating", "security", "pool", "sea_view",
    "terrace", "equipped_kitchen"
]

categorical_features = ["governorate", "city"]
target = "rent"

X = df[numeric_features + categorical_features].copy()
y = df[target].copy()

# -------------------------------------------------
# 3. Train / Test split
# -------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)
print(f"Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")

# -------------------------------------------------
# 4. Preprocessing
# -------------------------------------------------
preprocessor = ColumnTransformer(
    transformers=[
        ("num", "passthrough", numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
    ]
)

X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

print("Processed shape:", X_train_processed.shape)

# -------------------------------------------------
# 5. Monotonic constraints
# -------------------------------------------------
# Order of features after preprocessing:
# [surface, bedrooms, bathrooms, is_house, furnished, parking, elevator,
#  aircon, heating, security, pool, sea_view, terrace, equipped_kitchen,
#  + all one-hot columns]

# We force:
# surface   → +1 (must increase)
# bedrooms  → +1 (must increase)
# everything else → 0 (no constraint)

n_numeric = len(numeric_features)
n_total_features = X_train_processed.shape[1]

monotone_constraints = [0] * n_total_features
monotone_constraints[0] = 1   # surface
monotone_constraints[1] = 1   # bedrooms

print("\nMonotonic constraints applied on: surface and bedrooms")

# -------------------------------------------------
# 6. Train XGBoost
# -------------------------------------------------
print("\nTraining XGBoost with monotonic constraints...")

model = XGBRegressor(
    n_estimators=400,
    max_depth=7,
    learning_rate=0.07,
    subsample=0.8,
    colsample_bytree=0.8,
    monotone_constraints=tuple(monotone_constraints),
    random_state=42,
    n_jobs=-1,
    verbosity=0
)

model.fit(X_train_processed, y_train)

# -------------------------------------------------
# 7. Evaluation
# -------------------------------------------------
y_pred = model.predict(X_test_processed)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\n" + "=" * 60)
print("RESULTS - XGBoost + Monotonic Constraints")
print("=" * 60)
print(f"MAE  : {mae:.0f} TND")
print(f"RMSE : {rmse:.0f} TND")
print(f"R²   : {r2:.3f}")

# -------------------------------------------------
# 8. Save model + preprocessor
# -------------------------------------------------
# We save both because we need the preprocessor later
joblib.dump({
    "model": model,
    "preprocessor": preprocessor,
    "numeric_features": numeric_features,
    "categorical_features": categorical_features
}, SCRIPT_DIR / "model.pkl")

metadata = {
    "model_name": "XGBoost + Monotonic Constraints",
    "mae": round(mae, 1),
    "rmse": round(rmse, 1),
    "r2": round(r2, 3),
    "constraints": ["surface ↑", "bedrooms ↑"]
}

with open(SCRIPT_DIR / "model_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print(f"\nModel saved → {SCRIPT_DIR / 'model.pkl'}")
print("✅ Training completed!")