from src.predict import predict_fraud


# ============================================================
# PREDICTION SERVICE
# ============================================================

def analyze_transaction(transaction):

    """
    Sends transaction data to the existing
    FraudShield ML prediction pipeline.
    """

    result = predict_fraud(
        step=transaction.step,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        oldbalanceOrg=transaction.oldbalanceOrg,
        newbalanceOrig=transaction.newbalanceOrig,
        oldbalanceDest=transaction.oldbalanceDest,
        newbalanceDest=transaction.newbalanceDest,
        threshold=0.5
    )

    return result