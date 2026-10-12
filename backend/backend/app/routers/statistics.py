# ============================================================
# app/routers/statistics.py
# ============================================================
from statistics import median

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Property
from app.schemas import CityStat, StatisticsResponse

router = APIRouter(prefix="/api", tags=["Statistics"])


def _round(value, digits=2):
    return round(float(value), digits) if value is not None else 0.0


@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    total = db.query(func.count(Property.id)).scalar() or 0

    if total == 0:
        return StatisticsResponse(
            total_properties=0,
            average_rent=0,
            median_rent=0,
            min_rent=0,
            max_rent=0,
            average_surface=0,
            average_price_per_m2=0,
        )

    average_rent = db.query(func.avg(Property.rent)).scalar()
    min_rent = db.query(func.min(Property.rent)).scalar()
    max_rent = db.query(func.max(Property.rent)).scalar()
    average_surface = db.query(func.avg(Property.surface)).scalar()

    rents = [r[0] for r in db.query(Property.rent).all()]
    median_rent = median(rents) if rents else 0

    furnished_avg = (
        db.query(func.avg(Property.rent)).filter(Property.furnished.is_(True)).scalar()
    )
    unfurnished_avg = (
        db.query(func.avg(Property.rent)).filter(Property.furnished.is_(False)).scalar()
    )

    rows = (
        db.query(
            Property.city,
            func.count(Property.id),
            func.avg(Property.rent),
            func.avg(Property.surface),
        )
        .group_by(Property.city)
        .order_by(func.count(Property.id).desc())
        .all()
    )

    by_city = [
        CityStat(
            city=city,
            properties=count,
            average_rent=_round(avg_rent),
            average_surface=_round(avg_surf),
            average_price_per_m2=(
                _round(avg_rent / avg_surf) if avg_surf else 0.0
            ),
        )
        for city, count, avg_rent, avg_surf in rows
    ]

    return StatisticsResponse(
        total_properties=total,
        average_rent=_round(average_rent),
        median_rent=_round(median_rent),
        min_rent=_round(min_rent),
        max_rent=_round(max_rent),
        average_surface=_round(average_surface),
        average_price_per_m2=(
            _round(average_rent / average_surface) if average_surface else 0.0
        ),
        most_represented_city=by_city[0].city if by_city else None,
        furnished_average_rent=_round(furnished_avg),
        unfurnished_average_rent=_round(unfurnished_avg),
        by_city=by_city,
    )
