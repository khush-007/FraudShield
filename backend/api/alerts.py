from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import FraudAlert


# ============================================================
# API ROUTER
# ============================================================

router = APIRouter(
    prefix="/alerts",
    tags=["Fraud Alerts"]
)


# ============================================================
# GET ALL ALERTS
# ============================================================

@router.get("/")
def get_alerts(
    db: Session = Depends(get_db)
):

    alerts = (
        db.query(FraudAlert)
        .order_by(FraudAlert.created_at.desc())
        .all()
    )

    return alerts


# ============================================================
# GET ALERT BY ID
# ============================================================

@router.get("/{alert_id}")
def get_alert_by_id(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(FraudAlert)
        .filter(FraudAlert.id == alert_id)
        .first()
    )

    if alert is None:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    return alert


# ============================================================
# UPDATE ALERT STATUS
# ============================================================

@router.patch("/{alert_id}/status")
def update_alert_status(
    alert_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    # Find alert
    alert = (
        db.query(FraudAlert)
        .filter(FraudAlert.id == alert_id)
        .first()
    )

    if alert is None:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    # Allowed statuses
    allowed_statuses = [
        "OPEN",
        "INVESTIGATING",
        "RESOLVED",
        "FALSE_POSITIVE"
    ]

    if status.upper() not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values: {allowed_statuses}"
        )

    # Update status
    alert.status = status.upper()

    db.commit()

    db.refresh(alert)

    return alert

# ============================================================
# ADD / UPDATE ANALYST NOTES
# ============================================================

@router.patch("/{alert_id}/notes")
def update_alert_notes(
    alert_id: int,
    notes: str,
    db: Session = Depends(get_db)
):

    # Find alert
    alert = (
        db.query(FraudAlert)
        .filter(FraudAlert.id == alert_id)
        .first()
    )

    if alert is None:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    # Update analyst notes
    alert.analyst_notes = notes

    db.commit()

    db.refresh(alert)

    return alert