"""
TounesRent - Dataset Preparation
Final version: Step 1 + 2 + 3 + Merge
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re


def clean_tayara(script_dir: Path) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("STEP 2 – Cleaning tayara.csv")
    print("=" * 60)

    df = pd.read_csv(script_dir / "data" / "tayara.csv", low_memory=False)
    print("Original shape:", df.shape)

    df = df[df["transaction"].str.lower() == "rent"].copy()
    for col in ["price", "surface", "rooms", "bathrooms"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[(df["price"] >= 300) & (df["price"] <= 8000)].copy()
    df = df[(df["surface"] >= 30) & (df["surface"] <= 400)].copy()
    print("After filters:", df.shape)

    df = df.rename(columns={"price": "rent", "rooms": "bedrooms"})

    CITY_TO_GOV = {
        "Tunis": "Tunis", "La_Marsa": "Tunis", "La Marsa": "Tunis",
        "Gammarth": "Tunis", "Carthage": "Tunis", "Le_Bardo": "Tunis",
        "Le Bardo": "Tunis", "El_Menzah": "Tunis", "El Menzah": "Tunis",
        "L_Aouina": "Tunis", "L'Aouina": "Tunis", "Cite_El_Khadra": "Tunis",
        "Lac_1": "Tunis", "Lac 1": "Tunis", "Lac_2": "Tunis",
        "Ain_Zaghouan": "Tunis", "El_Kram": "Tunis", "La_Goulette": "Tunis",
        "Ariana": "Ariana", "La_Soukra": "Ariana", "La Soukra": "Ariana",
        "Raoued": "Ariana", "Ennasr": "Ariana", "Chotrana": "Ariana",
        "Borj_Louzir": "Ariana", "Mnihla": "Ariana",
        "Ben_Arous": "Ben Arous", "Ben Arous": "Ben Arous",
        "Ezzahra": "Ben Arous", "Rades": "Ben Arous", "Hammam_Lif": "Ben Arous",
        "El_Mourouj": "Ben Arous", "Megrine": "Ben Arous", "Bou_Mhel": "Ben Arous",
        "La_Manouba": "Manouba", "Manouba": "Manouba",
        "Nabeul": "Nabeul", "Hammamet": "Nabeul", "Kelibia": "Nabeul",
        "El_Haouaria": "Nabeul", "Korba": "Nabeul", "Soliman": "Nabeul",
        "Takelsa": "Nabeul", "Mrezga": "Nabeul",
        "Sousse": "Sousse", "Hammam_Sousse": "Sousse", "Akouda": "Sousse",
        "Msaken": "Sousse", "Hergla": "Sousse",
        "Sfax": "Sfax", "Monastir": "Monastir", "Mahdia": "Mahdia",
        "Bizerte": "Bizerte", "Gabes": "Gabès", "Medenine": "Médenine",
        "Kairouan": "Kairouan", "Gafsa": "Gafsa",
    }

    df["governorate"] = df["city"].map(CITY_TO_GOV).fillna(df["city"])

    text = (df["title"].fillna("") + " " + df["description"].fillna("")).str.lower()
    df["furnished"] = text.str.contains(r"meublé|meuble|furnished|semi.?meublé", regex=True).astype(int)
    df["parking"] = text.str.contains(r"garage|parking|abri.?voiture|place.?de.?parking", regex=True).astype(int)

    df["bedrooms"] = df["bedrooms"].fillna(2).round().clip(1, 6).astype(int)
    df["bathrooms"] = df["bathrooms"].fillna(1).round().clip(1, 4).astype(int)

    return pd.DataFrame({
        "governorate": df["governorate"],
        "city": df["city"].astype(str).str.replace("_", " "),
        "quartier": df["region"].fillna("Other"),
        "surface": df["surface"],
        "bedrooms": df["bedrooms"],
        "bathrooms": df["bathrooms"],
        "is_house": 0,
        "furnished": df["furnished"],
        "parking": df["parking"],
        "elevator": 0, "aircon": 0, "heating": 0, "security": 0,
        "pool": 0, "sea_view": 0, "terrace": 0, "equipped_kitchen": 0,
        "rent": df["rent"],
        "source": "tayara"
    })


def clean_tunisia_real_estate(script_dir: Path) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("STEP 3 – Cleaning tunisia-real-estate.csv")
    print("=" * 60)

    df = pd.read_csv(script_dir / "data" / "tunisia-real-estate.csv", low_memory=False)
    print("Original shape:", df.shape)

    df = df[df["Nature"].str.contains("Rental|rent", case=False, na=False)].copy()
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df["Surface"] = pd.to_numeric(df["Surface"], errors="coerce")

    df = df[(df["Price"] >= 300) & (df["Price"] <= 8000)].copy()
    df = df[(df["Surface"] >= 30) & (df["Surface"] <= 400)].copy()
    print("After filters:", df.shape)

    def extract_bedrooms(text):
        if pd.isna(text):
            return np.nan
        text = str(text).lower()
        match = re.search(r"(\d)-room", text)
        if match:
            return int(match.group(1))
        if "studio" in text:
            return 1
        return np.nan

    df["bedrooms"] = df["Type of Real Estate"].apply(extract_bedrooms)
    df["bedrooms"] = df["bedrooms"].fillna(2).round().clip(1, 6).astype(int)
    df["is_house"] = df["Type of Real Estate"].str.contains(
        "House|Villa|Duplex", case=False, na=False
    ).astype(int)

    return pd.DataFrame({
        "governorate": df["Governorate"].fillna("Unknown"),
        "city": df["Delegation"].fillna(df["Locality"]).fillna("Other"),
        "quartier": df["Locality"].fillna("Other"),
        "surface": df["Surface"],
        "bedrooms": df["bedrooms"],
        "bathrooms": 1,
        "is_house": df["is_house"],
        "furnished": 0,
        "parking": 0,
        "elevator": 0, "aircon": 0, "heating": 0, "security": 0,
        "pool": 0, "sea_view": 0, "terrace": 0, "equipped_kitchen": 0,
        "rent": df["Price"],
        "source": "tunisia-real-estate"
    })


if __name__ == "__main__":
    SCRIPT_DIR = Path(__file__).resolve().parent

    # ---------- STEP 1 ----------
    print("=" * 60)
    print("STEP 1 – Cleaning rentals_clean_2026.csv")
    print("=" * 60)

    df = pd.read_csv(SCRIPT_DIR / "data" / "rentals_clean_2026.csv")
    df = df[(df["rent"] >= 300) & (df["rent"] <= 8000)].copy()
    df = df[(df["surface"] >= 30) & (df["surface"] <= 400)].copy()
    df = df.rename(columns={"garage": "parking"})

    def surface_bucket(s):
        if s < 60: return "S"
        elif s < 90: return "M"
        elif s < 130: return "L"
        else: return "XL"

    df["surface_bucket"] = df["surface"].apply(surface_bucket)
    median_by_bucket = df.groupby("surface_bucket")["bedrooms"].median()
    df["bedrooms"] = df["bedrooms"].fillna(df["surface_bucket"].map(median_by_bucket))
    df["bedrooms"] = df["bedrooms"].fillna(df["bedrooms"].median()).round().astype(int)
    df["bathrooms"] = df["bathrooms"].fillna(1).round().astype(int)

    keep_cols = [
        "governorate", "city", "quartier", "surface", "bedrooms", "bathrooms",
        "is_house", "furnished", "parking", "elevator", "aircon", "heating",
        "security", "pool", "sea_view", "terrace", "equipped_kitchen", "rent"
    ]
    df_step1 = df[keep_cols].copy()
    df_step1["source"] = "rentals_clean_2026"
    print("Step 1 shape:", df_step1.shape)

    # ---------- STEP 2 ----------
    df_tayara = clean_tayara(SCRIPT_DIR)
    print("Step 2 shape:", df_tayara.shape)

    # ---------- STEP 3 ----------
    df_tre = clean_tunisia_real_estate(SCRIPT_DIR)
    print("Step 3 shape:", df_tre.shape)

    # ==================================================
    # STEP 5 – MERGE + FINAL CLEANING
    # ==================================================
    print("\n" + "=" * 60)
    print("STEP 5 – Merging all sources")
    print("=" * 60)

    df_final = pd.concat([df_step1, df_tayara, df_tre], ignore_index=True)
    print("After concat:", df_final.shape)

    # Remove exact duplicates
    before = len(df_final)
    df_final = df_final.drop_duplicates(
        subset=["surface", "bedrooms", "city", "rent"],
        keep="first"
    )
    print(f"Removed {before - len(df_final)} exact duplicates → {df_final.shape}")

    # Remove extreme price per m² outliers
    df_final["price_m2"] = df_final["rent"] / df_final["surface"]
    q1 = df_final["price_m2"].quantile(0.01)
    q99 = df_final["price_m2"].quantile(0.99)
    df_final = df_final[(df_final["price_m2"] >= q1) & (df_final["price_m2"] <= q99)].copy()
    df_final = df_final.drop(columns=["price_m2"])
    print("After price/m² outlier removal:", df_final.shape)

    # Harmonize governorate names
    df_final["governorate"] = (
        df_final["governorate"]
        .str.strip()
        .str.title()
        .replace({
            "Ben Arous": "Ben Arous",
            "Ben arous": "Ben Arous",
            "La Manouba": "Manouba",
            "Manouba": "Manouba",
            "Gabes": "Gabès",
            "Medenine": "Médenine",
        })
    )

    # Final quality check
    print("\n===== FINAL DATASET =====")
    print("Shape:", df_final.shape)
    print("\nNull %:")
    print((df_final.isnull().mean() * 100).round(1).sort_values(ascending=False))
    print("\nRent stats:")
    print(df_final["rent"].describe().round(0))
    print("\nSurface stats:")
    print(df_final["surface"].describe().round(0))
    print("\nBy source:")
    print(df_final["source"].value_counts())
    print("\nTop governorates:")
    print(df_final["governorate"].value_counts().head(10))
    print("\nTop cities:")
    print(df_final["city"].value_counts().head(12))

    # Save final dataset
    output = SCRIPT_DIR / "data" / "tunisian_rentals_final.csv"
    df_final.to_csv(output, index=False)
    print(f"\n✅ Final dataset saved → {output}")
    print("=" * 60)