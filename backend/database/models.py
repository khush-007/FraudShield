from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from backend.database.database import Base


# ============================================================
# TRANSACTION TABLE
# ============================================================

class Transaction(Base):

    __tablename__ = "transactions"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------------
    # TRANSACTION DETAILS
    # --------------------------------------------------------

    step = Column(
        Integer,
        nullable=False
    )

    transaction_type = Column(
        String,
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    # --------------------------------------------------------
    # SENDER BALANCES
    # --------------------------------------------------------

    oldbalanceOrg = Column(
        Float,
        nullable=False
    )

    newbalanceOrig = Column(
        Float,
        nullable=False
    )

    # --------------------------------------------------------
    # RECEIVER BALANCES
    # --------------------------------------------------------

    oldbalanceDest = Column(
        Float,
        nullable=False
    )

    newbalanceDest = Column(
        Float,
        nullable=False
    )

    # --------------------------------------------------------
    # ML FRAUD ANALYSIS
    # --------------------------------------------------------

    fraud_probability = Column(
        Float,
        nullable=False
    )

    # Fraud score from 0 to 100
    fraud_score = Column(
        Float,
        nullable=False,
        default=0
    )

    # 0 = NOT FRAUD
    # 1 = FRAUD
    is_fraud = Column(
        Integer,
        nullable=False,
        default=0
    )

    risk_level = Column(
        String,
        nullable=False
    )

    decision = Column(
        String,
        nullable=False
    )

    # Risk factors stored as text
    risk_factors = Column(
        String,
        nullable=True
    )

    # --------------------------------------------------------
    # TIMESTAMP
    # --------------------------------------------------------

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # --------------------------------------------------------
    # RELATIONSHIP WITH FRAUD ALERT
    # --------------------------------------------------------

    fraud_alert = relationship(
        "FraudAlert",
        back_populates="transaction",
        uselist=False
    )


# ============================================================
# FRAUD ALERT TABLE
# ============================================================

class FraudAlert(Base):

    __tablename__ = "fraud_alerts"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Link to transaction
    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id"),
        nullable=False
    )

    # --------------------------------------------------------
    # ALERT INFORMATION
    # --------------------------------------------------------

    status = Column(
        String,
        default="OPEN",
        nullable=False
    )

    analyst_notes = Column(
        String,
        nullable=True
    )

    # --------------------------------------------------------
    # TIMESTAMPS
    # --------------------------------------------------------

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationship
    transaction = relationship(
        "Transaction",
        back_populates="fraud_alert"
    )