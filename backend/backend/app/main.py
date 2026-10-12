# ============================================================
# app/main.py
# ============================================================
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registers the tables)
from app.database import Base, engine
from app.routers import predict, properties, statistics


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creates tables if they do not exist yet.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TounesRent API",
    description="Tunisian Rental Price Estimation Platform 🇹🇳",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(properties.router)
app.include_router(statistics.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "TounesRent API is running 🇹🇳", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
