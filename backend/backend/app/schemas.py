# ============================================================
# app/schemas.py
# ============================================================
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# -------------------------
# Property schemas
# -------------------------


class PropertyBase(BaseModel):
    governorate: str = Field(..., min_length=2, max_length=80, examples=["Ariana"])
    city: str = Field(..., min_length=2, max_length=120, examples=["Ariana Ville"])
    surface: float = Field(..., gt=0, le=2000, examples=[90])
    bedrooms: int = Field(..., ge=1, le=15, examples=[2])
    bathrooms: int = Field(1, ge=1, le=10, examples=[1])
    floor: Optional[int] = Field(None, ge=-5, le=60, examples=[2])
    condition: Optional[str] = Field("good", examples=["good"])

    is_house: bool = False
    furnished: bool = False
    parking: bool = False
    elevator: bool = False
    aircon: bool = False
    heating: bool = False
    security: bool = False
    pool: bool = False
    sea_view: bool = False
    terrace: bool = False
    equipped_kitchen: bool = False


class PropertyCreate(PropertyBase):
    rent: float = Field(..., gt=0, examples=[950])


class PropertyUpdate(BaseModel):
    governorate: Optional[str] = None
    city: Optional[str] = None
    surface: Optional[float] = Field(None, gt=0)
    bedrooms: Optional[int] = Field(None, ge=1)
    bathrooms: Optional[int] = Field(None, ge=1)
    floor: Optional[int] = None
    condition: Optional[str] = None

    is_house: Optional[bool] = None
    furnished: Optional[bool] = None
    parking: Optional[bool] = None
    elevator: Optional[bool] = None
    aircon: Optional[bool] = None
    heating: Optional[bool] = None
    security: Optional[bool] = None
    pool: Optional[bool] = None
    sea_view: Optional[bool] = None
    terrace: Optional[bool] = None
    equipped_kitchen: Optional[bool] = None

    rent: Optional[float] = Field(None, gt=0)


class PropertyOut(PropertyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rent: float
    price_per_m2: Optional[float] = None
    created_at: datetime


# -------------------------
# Prediction schemas
# -------------------------


class PredictRequest(BaseModel):
    governorate: str = Field(..., examples=["Ariana"])
    city: str = Field(..., examples=["Ariana Ville"])
    surface: float = Field(..., gt=0, le=2000, examples=[90])
    bedrooms: int = Field(..., ge=1, le=15, examples=[2])
    bathrooms: int = Field(1, ge=1, le=10, examples=[1])

    is_house: bool = False
    furnished: bool = False
    parking: bool = True
    elevator: bool = False
    aircon: bool = False
    heating: bool = False
    security: bool = False
    pool: bool = False
    sea_view: bool = False
    terrace: bool = False
    equipped_kitchen: bool = False

    advertised_price: Optional[float] = Field(None, gt=0, examples=[1200])


class PredictResponse(BaseModel):
    estimated_rent: int
    min_rent: int
    max_rent: int
    currency: str = "TND"
    price_per_m2: Optional[float] = None
    confidence: Optional[str] = None
    message: Optional[str] = None
    similar_properties: List[PropertyOut] = []


# -------------------------
# Statistics schemas
# -------------------------


class CityStat(BaseModel):
    city: str
    properties: int
    average_rent: float
    average_surface: float
    average_price_per_m2: float


class StatisticsResponse(BaseModel):
    total_properties: int
    average_rent: float
    median_rent: float
    min_rent: float
    max_rent: float
    average_surface: float
    average_price_per_m2: float
    most_represented_city: Optional[str] = None
    furnished_average_rent: float = 0
    unfurnished_average_rent: float = 0
    by_city: List[CityStat] = []
