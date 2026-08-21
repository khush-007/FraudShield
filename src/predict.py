import os
import joblib
import pandas as pd


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "xgboost_fraud_model.joblib"
)

PREPROCESSOR_PATH = os.path.join(
    BASE_DIR,
    "models",
    "preprocessor.joblib"
)


# =========================================================
# LOAD MODEL AND PREPROCESSOR
# =========================================================

model = joblib.load(MODEL_PATH)

preprocessor = joblib.load(PREPROCESSOR_PATH)


# =========================================================
# FEATURE ENGINEERING
# =========================================================

def create_features(transaction_df):

    df = transaction_df.copy()

    # Sender balance error
    df["sender_balance_error"] = (
        df["oldbalanceOrg"]
        - df["amount"]
        - df["newbalanceOrig"]
    ).abs()

    # Receiver balance error
    df["receiver_balance_error"] = (
        df["oldbalanceDest"]
        + df["amount"]
        - df["newbalanceDest"]
    ).abs()

    # Origin account empty after transaction
    df["origin_empty_after"] = (
        df["newbalanceOrig"] == 0
    ).astype(int)

    # Destination account empty before transaction
    df["destination_empty_before"] = (
        df["oldbalanceDest"] == 0
    ).astype(int)

    # Amount compared to sender's original balance
    df["amount_to_origin_balance"] = (
        df["amount"]
        / df["oldbalanceOrg"].replace(0, 1)
    )

    return df


# =========================================================
# RISK FACTOR ANALYSIS
# =========================================================

def get_risk_factors(
    transaction_type,
    amount,
    oldbalanceOrg,
    newbalanceOrig,
    oldbalanceDest,
    fraud_probability
):

    risk_factors = []

    # High transaction amount
    if amount >= 100000:

        risk_factors.append(
            "High transaction amount detected"
        )

    # Very large transaction
    if amount >= 500000:

        risk_factors.append(
            "Very large transaction amount"
        )

    # Sender account becomes empty
    if oldbalanceOrg > 0 and newbalanceOrig == 0:

        risk_factors.append(
            "Sender account balance becomes zero"
        )

    # Transaction uses most of sender balance
    if oldbalanceOrg > 0:

        amount_ratio = amount / oldbalanceOrg

        if amount_ratio >= 0.90:

            risk_factors.append(
                "Transaction uses more than 90% of sender balance"
            )

    # Empty destination account
    if oldbalanceDest == 0:

        risk_factors.append(
            "Destination account had zero balance before transaction"
        )

    # Higher-risk transaction types
    if transaction_type in ["TRANSFER", "CASH_OUT"]:

        risk_factors.append(
            f"{transaction_type} transaction requires additional monitoring"
        )

    # Strong ML model signal
    if fraud_probability >= 0.90:

        risk_factors.append(
            "ML model detected extremely high fraud probability"
        )

    elif fraud_probability >= 0.50:

        risk_factors.append(
            "ML model detected high fraud probability"
        )

    elif fraud_probability >= 0.10:

        risk_factors.append(
            "ML model detected moderate fraud probability"
        )

    # Safe transaction explanation
    if not risk_factors:

        risk_factors.append(
            "No significant fraud risk factors detected"
        )

    return risk_factors


# =========================================================
# FRAUD PREDICTION
# =========================================================

def predict_fraud(
    step,
    transaction_type,
    amount,
    oldbalanceOrg,
    newbalanceOrig,
    oldbalanceDest,
    newbalanceDest,
    threshold=0.5
):

    # =====================================================
    # CREATE TRANSACTION DATAFRAME
    # =====================================================

    transaction = pd.DataFrame([{
        "step": step,
        "type": transaction_type,
        "amount": amount,
        "oldbalanceOrg": oldbalanceOrg,
        "newbalanceOrig": newbalanceOrig,
        "oldbalanceDest": oldbalanceDest,
        "newbalanceDest": newbalanceDest
    }])


    # =====================================================
    # FEATURE ENGINEERING
    # =====================================================

    transaction = create_features(transaction)

    feature_columns = [
        "step",
        "type",
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "sender_balance_error",
        "receiver_balance_error",
        "origin_empty_after",
        "destination_empty_before",
        "amount_to_origin_balance"
    ]

    transaction = transaction[feature_columns]


    # =====================================================
    # PREPROCESSING
    # =====================================================

    transaction_processed = preprocessor.transform(
        transaction
    )


    # =====================================================
    # ML FRAUD PROBABILITY
    # =====================================================

    ml_fraud_probability = float(
        model.predict_proba(
            transaction_processed
        )[0][1]
    )


    # =====================================================
    # RULE-BASED RISK SCORE
    # =====================================================

    rule_score = 0.0

    # Very high transaction amount
    if amount >= 500000:
        rule_score += 0.25

    # High transaction amount
    elif amount >= 100000:
        rule_score += 0.10

    # Sender account becomes empty
    if oldbalanceOrg > 0 and newbalanceOrig == 0:
        rule_score += 0.25

    # Transaction uses more than 90% of balance
    if oldbalanceOrg > 0:

        amount_ratio = amount / oldbalanceOrg

        if amount_ratio >= 0.90:
            rule_score += 0.20

    # Receiver had zero balance before transaction
    if oldbalanceDest == 0:
        rule_score += 0.15

    # Higher-risk transaction type
    if transaction_type in ["TRANSFER", "CASH_OUT"]:
        rule_score += 0.15

    # Maximum rule score = 1.0
    rule_score = min(rule_score, 1.0)


    # =====================================================
    # FINAL HYBRID FRAUD SCORE
    # =====================================================

    fraud_probability = max(
        ml_fraud_probability,
        rule_score
    )


    # =====================================================
    # FINAL PREDICTION
    # =====================================================

    prediction = int(
        fraud_probability >= threshold
    )


    # =====================================================
    # RISK LEVEL AND DECISION
    # =====================================================

    if fraud_probability >= 0.90:

        risk_level = "CRITICAL"
        decision = "BLOCK TRANSACTION"

    elif fraud_probability >= 0.50:

        risk_level = "HIGH"
        decision = "FLAG FOR REVIEW"

    elif fraud_probability >= 0.25:

        risk_level = "MEDIUM"
        decision = "MONITOR TRANSACTION"

    else:

        risk_level = "LOW"
        decision = "ALLOW TRANSACTION"


    # =====================================================
    # RISK FACTORS
    # =====================================================

    risk_factors = get_risk_factors(
        transaction_type=transaction_type,
        amount=amount,
        oldbalanceOrg=oldbalanceOrg,
        newbalanceOrig=newbalanceOrig,
        oldbalanceDest=oldbalanceDest,
        fraud_probability=fraud_probability
    )


    # =====================================================
    # RETURN RESULTS
    # =====================================================

    return {

        "fraud_probability": round(
            float(fraud_probability),
            6
        ),

        "fraud_percentage": round(
            float(fraud_probability * 100),
            2
        ),

        "fraud_score": round(
            float(fraud_probability * 100),
            2
        ),

        "prediction": prediction,

        "is_fraud": bool(prediction),

        "risk_level": risk_level,

        "decision": decision,

        "risk_factors": risk_factors,

        "threshold_used": threshold,

        # Optional: useful for debugging
        "ml_fraud_probability": round(
            ml_fraud_probability,
            6
        ),

        "rule_score": round(
            rule_score,
            6
        )
    }