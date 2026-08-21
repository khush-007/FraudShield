from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ============================================================
# INPUT SCHEMA
# ============================================================

class TransactionCreate(BaseModel):

    step: int = Field(
        ...,
        ge=1,
        description="Transaction time step"
    )

    transaction_type: str

    amount: float = Field(
        ...,
        ge=0,
        description="Transaction amount"
    )

    oldbalanceOrg: float = Field(
        ...,
        ge=0
    )

    newbalanceOrig: float = Field(
        ...,
        ge=0
    )

    oldbalanceDest: float = Field(
        ...,
        ge=0
    )

    newbalanceDest: float = Field(
        ...,
        ge=0
    )


# ============================================================
# TRANSACTION RESPONSE SCHEMA
# ============================================================

class TransactionResponse(TransactionCreate):

    id: int

    # ML prediction results
    fraud_probability: float

    fraud_score: float

    is_fraud: bool

    risk_level: str

    decision: str

    risk_factors: List[str]

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# ============================================================
# FRAUD ALERT RESPONSE SCHEMA
# ============================================================

class FraudAlertResponse(BaseModel):

    id: int

    transaction_id: int

    status: str

    analyst_notes: Optional[str] = None

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }