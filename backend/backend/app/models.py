# ============================================================
# app/models.py
# ============================================================
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    governorate = Column(String(80), nullable=False, index=True)
    city = Column(String(120), nullable=False, index=True)

    surface = Column(Float, nullable=False)
    bedrooms = Column(Integer, nullable=False, default=1)
    bathrooms = Column(Integer, nullable=False, default=1)
    floor = Column(Integer, nullable=True)
    condition = Column(String(30), nullable=True, default="good")

    is_house = Column(Boolean, nullable=False, default=False)
    furnished = Column(Boolean, nullable=False, default=False)
    parking = Column(Boolean, nullable=False, default=False)
    elevator = Column(Boolean, nullable=False, default=False)
    aircon = Column(Boolean, nullable=False, default=False)
    heating = Column(Boolean, nullable=False, default=False)
    security = Column(Boolean, nullable=False, default=False)
    pool = Column(Boolean, nullable=False, default=False)
    sea_view = Column(Boolean, nullable=False, default=False)
    terrace = Column(Boolean, nullable=False, default=False)
    equipped_kitchen = Column(Boolean, nullable=False, default=False)

    rent = Column(Float, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    predictions = relationship(
        "Prediction", back_populates="property", cascade="all, delete-orphan"
    )

    @property
    def price_per_m2(self) -> float | None:
        if not self.surface:
            return None
        return round(self.rent / self.surface, 2)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(
        Integer, ForeignKey("properties.id", ondelete="SET NULL"), nullable=True
    )

    # input snapshot (so we can audit predictions later)
    governorate = Column(String(80), nullable=True)
    city = Column(String(120), nullable=True)
    surface = Column(Float, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    furnished = Column(Boolean, nullable=True)
    parking = Column(Boolean, nullable=True)

    # output
    estimated_rent = Column(Float, nullable=False)
    min_rent = Column(Float, nullable=False)
    max_rent = Column(Float, nullable=False)
    advertised_price = Column(Float, nullable=True)
    model_name = Column(String(60), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    property = relationship("Property", back_populates="predictions")
