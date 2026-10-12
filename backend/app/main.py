from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import engine

from backend.app.database import Base
from backend.app.routers import predict, properties, statistics
from app.schemas import PredictRequest, PredictResponse


# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TounesRent API",
    version="1.0.0",
    description="Tunisian rental price estimation platform 🇹🇳",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(properties.router)
app.include_router(statistics.router)

@app.get("/")
def root():
    return {"app": "TounesRent", "status": "ok", "docs": "/docs"}