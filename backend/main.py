import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.database import Base, engine
from backend.database import models

from backend.api.transactions import router as transactions_router
from backend.api.alerts import router as alerts_router
from backend.api.analytics import router as analytics_router


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="FraudShield API",
    description="AI-powered financial fraud detection and risk intelligence API",
    version="1.0.0"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Add deployed frontend URL from environment variable
frontend_url = os.getenv("FRONTEND_URL")

if frontend_url:
    allowed_origins.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REGISTER API ROUTERS
# ============================================================

app.include_router(transactions_router)
app.include_router(alerts_router)
app.include_router(analytics_router)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Welcome to FraudShield API",
        "status": "running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "FraudShield Backend"
    }