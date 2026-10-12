# ============================================================
# app/routers/properties.py
# ============================================================
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import find_similar_properties
from app.database import get_db
from app.models import Property
from app.schemas import PropertyCreate, PropertyOut, PropertyUpdate

router = APIRouter(prefix="/api/properties", tags=["Properties"])


# IMPORTANT: /similar must be declared BEFORE /{property_id}
@router.get("/similar", response_model=List[PropertyOut])
def similar_properties(
    governorate: Optional[str] = None,
    city: Optional[str] = None,
    surface: Optional[float] = Query(None, gt=0),
    bedrooms: Optional[int] = Query(None, ge=1),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    return find_similar_properties(
        db,
        governorate=governorate,
        city=city,
        surface=surface,
        bedrooms=bedrooms,
        limit=limit,
    )


@router.get("", response_model=List[PropertyOut])
def list_properties(
    governorate: Optional[str] = None,
    city: Optional[str] = None,
    min_rent: Optional[float] = Query(None, ge=0),
    max_rent: Optional[float] = Query(None, ge=0),
    min_surface: Optional[float] = Query(None, gt=0),
    max_surface: Optional[float] = Query(None, gt=0),
    bedrooms: Optional[int] = Query(None, ge=1),
    furnished: Optional[bool] = None,
    parking: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Property)
    if governorate:
        q = q.filter(Property.governorate.ilike(governorate))
    if city:
        q = q.filter(Property.city.ilike(city))
    if min_rent is not None:
        q = q.filter(Property.rent >= min_rent)
    if max_rent is not None:
        q = q.filter(Property.rent <= max_rent)
    if min_surface is not None:
        q = q.filter(Property.surface >= min_surface)
    if max_surface is not None:
        q = q.filter(Property.surface <= max_surface)
    if bedrooms is not None:
        q = q.filter(Property.bedrooms == bedrooms)
    if furnished is not None:
        q = q.filter(Property.furnished == furnished)
    if parking is not None:
        q = q.filter(Property.parking == parking)

    return q.order_by(Property.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{property_id}", response_model=PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.post("", response_model=PropertyOut, status_code=201)
def create_property(payload: PropertyCreate, db: Session = Depends(get_db)):
    prop = Property(**payload.model_dump())
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.put("/{property_id}", response_model=PropertyOut)
def update_property(
    property_id: int, payload: PropertyUpdate, db: Session = Depends(get_db)
):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prop, field, value)

    db.commit()
    db.refresh(prop)
    return prop


@router.delete("/{property_id}", status_code=204)
def delete_property(property_id: int, db: Session = Depends(get_db)):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    db.delete(prop)
    db.commit()
    return None

@router.get("", response_model=List[PropertyOut])
def list_properties(
    governorate: Optional[str] = None,
    city: Optional[str] = None,
    min_rent: Optional[float] = Query(None, ge=0),
    max_rent: Optional[float] = Query(None, ge=0),
    min_surface: Optional[float] = Query(None, gt=0),
    max_surface: Optional[float] = Query(None, gt=0),
    bedrooms: Optional[int] = Query(None, ge=1),
    furnished: Optional[bool] = None,
    parking: Optional[bool] = None,
    elevator: Optional[bool] = None,
    aircon: Optional[bool] = None,
    heating: Optional[bool] = None,
    security: Optional[bool] = None,
    pool: Optional[bool] = None,
    sea_view: Optional[bool] = None,
    terrace: Optional[bool] = None,
    equipped_kitchen: Optional[bool] = None,
    is_house: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Property)

    if governorate:
        q = q.filter(Property.governorate.ilike(governorate))
    if city:
        q = q.filter(Property.city.ilike(f"%{city}%"))
    if min_rent is not None:
        q = q.filter(Property.rent >= min_rent)
    if max_rent is not None:
        q = q.filter(Property.rent <= max_rent)
    if min_surface is not None:
        q = q.filter(Property.surface >= min_surface)
    if max_surface is not None:
        q = q.filter(Property.surface <= max_surface)
    if bedrooms is not None:
        q = q.filter(Property.bedrooms == bedrooms)

    bool_filters = {
        "furnished": furnished,
        "parking": parking,
        "elevator": elevator,
        "aircon": aircon,
        "heating": heating,
        "security": security,
        "pool": pool,
        "sea_view": sea_view,
        "terrace": terrace,
        "equipped_kitchen": equipped_kitchen,
        "is_house": is_house,
    }
    for field, value in bool_filters.items():
        if value is not None:
            q = q.filter(getattr(Property, field) == value)

    return q.order_by(Property.created_at.desc()).offset(skip).limit(limit).all()    
