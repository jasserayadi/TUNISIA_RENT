# ============================================================
# app/crud.py
# ============================================================
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.models import Property


def find_similar_properties(
    db: Session,
    *,
    governorate: Optional[str] = None,
    city: Optional[str] = None,
    surface: Optional[float] = None,
    bedrooms: Optional[int] = None,
    limit: int = 5,
) -> Sequence[Property]:
    """Return the properties that best match the given characteristics."""

    def _query(scope_city: Optional[str], scope_gov: Optional[str]):
        q = db.query(Property)
        if scope_city:
            q = q.filter(Property.city.ilike(scope_city))
        elif scope_gov:
            q = q.filter(Property.governorate.ilike(scope_gov))
        if surface:
            q = q.filter(Property.surface.between(surface * 0.7, surface * 1.3))
        if bedrooms is not None:
            q = q.filter(
                Property.bedrooms.between(max(1, bedrooms - 1), bedrooms + 1)
            )
        return q.limit(300).all()

    candidates = _query(city, governorate)

    # widen the search if the exact city has too few matches
    if len(candidates) < limit and city:
        extra = _query(None, governorate)
        seen = {p.id for p in candidates}
        candidates = list(candidates) + [p for p in extra if p.id not in seen]

    if not candidates:
        return []

    def score(p: Property) -> float:
        s = 0.0
        if surface:
            s += abs(p.surface - surface)
        if bedrooms is not None:
            s += abs(p.bedrooms - bedrooms) * 15
        if city and p.city.lower() != city.lower():
            s += 25
        return s

    candidates.sort(key=score)
    return candidates[:limit]
