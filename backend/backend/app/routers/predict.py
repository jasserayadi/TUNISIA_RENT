# ============================================================
# app/routers/predict.py
# ============================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import find_similar_properties
from app.database import get_db
from app.ml_service import ml_service
from app.models import Prediction
from app.schemas import PredictRequest, PredictResponse

router = APIRouter(prefix="/api", tags=["Prediction"])

RANGE_FACTOR = 0.15  # ±15 %


@router.post("/predict", response_model=PredictResponse)
def predict_rent(data: PredictRequest, db: Session = Depends(get_db)):
    payload = data.model_dump()

    try:
        raw = ml_service.predict(payload)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Prediction error: {exc}") from exc

    if raw <= 0 or raw != raw:  # negative or NaN
        raise HTTPException(status_code=400, detail="Prediction error: invalid model output")

    estimated = int(round(raw))
    min_rent = int(round(raw * (1 - RANGE_FACTOR)))
    max_rent = int(round(raw * (1 + RANGE_FACTOR)))

    # ---- advertised price evaluation ----
    message = None
    if data.advertised_price is not None:
        if data.advertised_price > max_rent:
            message = "⚠ The advertised price is above the estimated range."
        elif data.advertised_price < min_rent:
            message = "✓ The advertised price is below the estimated range (good deal)."
        else:
            message = "✓ The advertised price is within the estimated range."

    # ---- similar properties ----
    similar = find_similar_properties(
        db,
        governorate=data.governorate,
        city=data.city,
        surface=data.surface,
        bedrooms=data.bedrooms,
        limit=5,
    )

    confidence = "high" if len(similar) >= 5 else "medium" if len(similar) >= 2 else "low"

    # ---- persist the prediction ----
    db.add(
        Prediction(
            governorate=data.governorate,
            city=data.city,
            surface=data.surface,
            bedrooms=data.bedrooms,
            bathrooms=data.bathrooms,
            furnished=data.furnished,
            parking=data.parking,
            estimated_rent=estimated,
            min_rent=min_rent,
            max_rent=max_rent,
            advertised_price=data.advertised_price,
            model_name=ml_service.model_name,
        )
    )
    db.commit()

    return PredictResponse(
        estimated_rent=estimated,
        min_rent=min_rent,
        max_rent=max_rent,
        currency="TND",
        price_per_m2=round(estimated / data.surface, 2) if data.surface else None,
        confidence=confidence,
        message=message,
        similar_properties=similar,
    )
