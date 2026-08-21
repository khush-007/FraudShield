import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import Transaction, FraudAlert

from backend.schemas.transaction import (
    TransactionCreate,
    TransactionResponse
)

from backend.services.prediction_service import analyze_transaction


# ============================================================
# API ROUTER
# ============================================================

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


# ============================================================
# HELPER: CONVERT DATABASE TRANSACTION TO RESPONSE
# ============================================================

def transaction_to_response(transaction):

    risk_factors = []

    if transaction.risk_factors:
        try:
            risk_factors = json.loads(
                transaction.risk_factors
            )
        except json.JSONDecodeError:
            risk_factors = []

    return {
        "id": transaction.id,
        "step": transaction.step,
        "transaction_type": transaction.transaction_type,
        "amount": transaction.amount,
        "oldbalanceOrg": transaction.oldbalanceOrg,
        "newbalanceOrig": transaction.newbalanceOrig,
        "oldbalanceDest": transaction.oldbalanceDest,
        "newbalanceDest": transaction.newbalanceDest,

        "fraud_probability": transaction.fraud_probability,
        "fraud_score": transaction.fraud_score,
        "is_fraud": bool(transaction.is_fraud),

        "risk_level": transaction.risk_level,
        "decision": transaction.decision,

        "risk_factors": risk_factors,

        "created_at": transaction.created_at
    }


# ============================================================
# ANALYZE TRANSACTION
# ============================================================

@router.post(
    "/analyze",
    response_model=TransactionResponse
)
def analyze_new_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # 1. SEND TRANSACTION TO ML MODEL
    # --------------------------------------------------------

    try:

        result = analyze_transaction(transaction)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


    # --------------------------------------------------------
    # 2. CREATE TRANSACTION RECORD
    # --------------------------------------------------------

    db_transaction = Transaction(

        step=transaction.step,

        transaction_type=transaction.transaction_type,

        amount=transaction.amount,

        oldbalanceOrg=transaction.oldbalanceOrg,

        newbalanceOrig=transaction.newbalanceOrig,

        oldbalanceDest=transaction.oldbalanceDest,

        newbalanceDest=transaction.newbalanceDest,

        fraud_probability=result["fraud_probability"],

        fraud_score=result["fraud_score"],

        is_fraud=int(result["is_fraud"]),

        risk_level=result["risk_level"],

        decision=result["decision"],

        risk_factors=json.dumps(
            result["risk_factors"]
        )
    )


    # --------------------------------------------------------
    # 3. SAVE TRANSACTION
    # --------------------------------------------------------

    db.add(db_transaction)

    db.commit()

    db.refresh(db_transaction)


    # --------------------------------------------------------
    # 4. CREATE FRAUD ALERT FOR HIGH-RISK TRANSACTIONS
    # --------------------------------------------------------

    if result["risk_level"] in ["HIGH", "CRITICAL"]:

        fraud_alert = FraudAlert(

            transaction_id=db_transaction.id,

            status="OPEN"
        )

        db.add(fraud_alert)

        db.commit()


    # --------------------------------------------------------
    # 5. RETURN COMPLETE RESULT
    # --------------------------------------------------------

    return transaction_to_response(
        db_transaction
    )


# ============================================================
# GET ALL TRANSACTIONS
# ============================================================

@router.get(
    "/",
    response_model=list[TransactionResponse]
)
def get_transactions(
    db: Session = Depends(get_db)
):

    transactions = (
        db.query(Transaction)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    return [
        transaction_to_response(transaction)
        for transaction in transactions
    ]


# ============================================================
# GET TRANSACTION BY ID
# ============================================================

@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse
)
def get_transaction_by_id(
    transaction_id: int,
    db: Session = Depends(get_db)
):

    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id
        )
        .first()
    )

    if transaction is None:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction_to_response(
        transaction
    )