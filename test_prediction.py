from src.predict import predict_fraud


# ==========================================
# TEST 1: NORMAL TRANSACTION
# ==========================================

normal_transaction = predict_fraud(
    step=100,
    transaction_type="PAYMENT",
    amount=5000,
    oldbalanceOrg=20000,
    newbalanceOrig=15000,
    oldbalanceDest=50000,
    newbalanceDest=55000
)

print("\nNORMAL TRANSACTION")
print("=" * 50)

for key, value in normal_transaction.items():
    print(f"{key}: {value}")


# ==========================================
# TEST 2: SUSPICIOUS TRANSACTION
# ==========================================

suspicious_transaction = predict_fraud(
    step=200,
    transaction_type="TRANSFER",
    amount=500000,
    oldbalanceOrg=500000,
    newbalanceOrig=0,
    oldbalanceDest=0,
    newbalanceDest=0
)

print("\nSUSPICIOUS TRANSACTION")
print("=" * 50)

for key, value in suspicious_transaction.items():
    print(f"{key}: {value}")