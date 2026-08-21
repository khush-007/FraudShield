from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import Transaction, FraudAlert


# ============================================================
# API ROUTER
# ============================================================

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# ============================================================
# ANALYTICS SUMMARY
# ============================================================

@router.get("/summary")
def get_analytics_summary(
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # TOTAL TRANSACTIONS
    # --------------------------------------------------------

    total_transactions = (
        db.query(Transaction)
        .count()
    )


    # --------------------------------------------------------
    # RISK LEVEL COUNTS
    # --------------------------------------------------------

    low_risk = (
        db.query(Transaction)
        .filter(Transaction.risk_level == "LOW")
        .count()
    )

    medium_risk = (
        db.query(Transaction)
        .filter(Transaction.risk_level == "MEDIUM")
        .count()
    )

    high_risk = (
        db.query(Transaction)
        .filter(Transaction.risk_level == "HIGH")
        .count()
    )

    critical_risk = (
        db.query(Transaction)
        .filter(Transaction.risk_level == "CRITICAL")
        .count()
    )


    # --------------------------------------------------------
    # FRAUD RATE
    # --------------------------------------------------------

    fraud_transactions = high_risk + critical_risk

    fraud_rate = 0

    if total_transactions > 0:

        fraud_rate = round(
            (fraud_transactions / total_transactions) * 100,
            2
        )


    # --------------------------------------------------------
    # ALERT COUNTS
    # --------------------------------------------------------

    total_alerts = (
        db.query(FraudAlert)
        .count()
    )

    open_alerts = (
        db.query(FraudAlert)
        .filter(FraudAlert.status == "OPEN")
        .count()
    )

    investigating_alerts = (
        db.query(FraudAlert)
        .filter(FraudAlert.status == "INVESTIGATING")
        .count()
    )

    resolved_alerts = (
        db.query(FraudAlert)
        .filter(FraudAlert.status == "RESOLVED")
        .count()
    )


    # --------------------------------------------------------
    # RETURN ANALYTICS
    # --------------------------------------------------------

    return {

        "total_transactions": total_transactions,

        "fraud_transactions": fraud_transactions,

        "fraud_rate": fraud_rate,

        "risk_distribution": {

            "low": low_risk,
            "medium": medium_risk,
            "high": high_risk,
            "critical": critical_risk

        },

        "alerts": {

            "total": total_alerts,
            "open": open_alerts,
            "investigating": investigating_alerts,
            "resolved": resolved_alerts

        }

    }