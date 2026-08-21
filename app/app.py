import os
import sys
import streamlit as st


# ============================================================
# PROJECT PATH SETUP
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


from src.predict import predict_fraud


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FraudShield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #0E1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 1.1rem;
        color: #A0A0A0;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .card {
        background-color: #171B26;
        border: 1px solid #2A3140;
        border-radius: 12px;
        padding: 20px;
        min-height: 125px;
    }

    .card-label {
        font-size: 0.85rem;
        color: #A0A0A0;
        margin-bottom: 8px;
    }

    .card-value {
        font-size: 2rem;
        font-weight: 750;
    }

    .card-low {
        color: #2ECC71;
    }

    .card-medium {
        color: #F1C40F;
    }

    .card-high {
        color: #E67E22;
    }

    .card-critical {
        color: #FF4B4B;
    }

    .indicator-card {
        background-color: #171B26;
        border: 1px solid #2A3140;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 10px;
    }

    .recommendation {
        padding: 20px;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_risk_color(risk_level):

    colors = {
        "LOW": "card-low",
        "MEDIUM": "card-medium",
        "HIGH": "card-high",
        "CRITICAL": "card-critical"
    }

    return colors.get(risk_level, "")


def get_confidence(probability):

    confidence = max(probability, 1 - probability)

    if confidence >= 0.90:
        return "HIGH"

    elif confidence >= 0.70:
        return "MEDIUM"

    return "LOW"


def get_fraud_indicators(
    transaction_type,
    amount,
    oldbalanceOrg,
    newbalanceOrig,
    oldbalanceDest,
    newbalanceDest
):

    indicators = []

    # Transaction type
    if transaction_type == "TRANSFER":
        indicators.append(
            "⚠️ Transaction type is TRANSFER, which is associated with fraud patterns in the training data."
        )

    elif transaction_type == "CASH_OUT":
        indicators.append(
            "⚠️ Transaction type is CASH_OUT, which is associated with fraud patterns in the training data."
        )

    # Sender emptied account
    if oldbalanceOrg > 0 and newbalanceOrig == 0:
        indicators.append(
            "⚠️ Sender account balance becomes zero after the transaction."
        )

    # Amount equals sender balance
    if oldbalanceOrg > 0:

        ratio = amount / oldbalanceOrg

        if 0.95 <= ratio <= 1.05:
            indicators.append(
                "⚠️ Transaction amount is approximately equal to the sender's available balance."
            )

    # Empty destination
    if oldbalanceDest == 0:
        indicators.append(
            "⚠️ Receiver account had zero balance before the transaction."
        )

    # Large transaction
    if amount >= 1_000_000:
        indicators.append(
            "⚠️ Transaction amount is unusually large."
        )

    # Balance mismatch
    sender_expected = max(oldbalanceOrg - amount, 0)

    if abs(newbalanceOrig - sender_expected) > 1:
        indicators.append(
            "⚠️ Sender balance transition does not exactly match the transaction amount."
        )

    receiver_expected = oldbalanceDest + amount

    if oldbalanceDest > 0 and abs(newbalanceDest - receiver_expected) > 1:
        indicators.append(
            "⚠️ Receiver balance transition does not exactly match the transaction amount."
        )

    return indicators


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🛡️ FraudShield")

    st.caption(
        "Financial Fraud Detection & Risk Intelligence System"
    )

    st.divider()

    st.subheader("System Information")

    st.write("**Model**")
    st.caption("XGBoost Classifier")

    st.write("**Dataset**")
    st.caption("PaySim Financial Transaction Dataset")

    st.write("**Processed Features**")
    st.caption("16 model input features")

    st.divider()

    st.subheader("How it works")

    st.caption(
        """
        1. Enter transaction details  
        2. Features are generated  
        3. Transaction is processed  
        4. XGBoost calculates fraud probability  
        5. FraudShield provides a risk decision
        """
    )

    st.divider()

    st.caption("FraudShield ML System")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">
        🛡️ FraudShield
    </div>

    <div class="subtitle">
        AI-Powered Financial Fraud Detection & Risk Intelligence System
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# TRANSACTION INPUT
# ============================================================

st.markdown(
    '<div class="section-title">Transaction Details</div>',
    unsafe_allow_html=True
)


left_col, right_col = st.columns(2)


# ---------------- LEFT COLUMN ----------------

with left_col:

    step = st.number_input(
        "Transaction Step",
        min_value=1,
        value=250
    )

    transaction_type = st.selectbox(
        "Transaction Type",
        [
            "PAYMENT",
            "TRANSFER",
            "CASH_OUT",
            "CASH_IN",
            "DEBIT"
        ]
    )

    amount = st.number_input(
        "Transaction Amount",
        min_value=0.0,
        value=5000.0,
        step=1000.0
    )

    st.markdown("#### Sender Information")

    oldbalanceOrg = st.number_input(
        "Sender Balance Before Transaction",
        min_value=0.0,
        value=50000.0,
        step=1000.0
    )

    newbalanceOrig = st.number_input(
        "Sender Balance After Transaction",
        min_value=0.0,
        value=0.0,
        step=1000.0
    )


# ---------------- RIGHT COLUMN ----------------

with right_col:

    st.markdown("#### Receiver Information")

    oldbalanceDest = st.number_input(
        "Receiver Balance Before Transaction",
        min_value=0.0,
        value=0.0,
        step=1000.0
    )

    newbalanceDest = st.number_input(
        "Receiver Balance After Transaction",
        min_value=0.0,
        value=0.0,
        step=1000.0
    )

    st.markdown("#### Detection Settings")

    threshold = st.slider(
        "Fraud Detection Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.01
    )

    st.caption(
        "Transactions with fraud probability above this threshold are classified as fraudulent."
    )


st.divider()


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze = st.button(
    "🔍 ANALYZE TRANSACTION",
    use_container_width=True,
    type="primary"
)


# ============================================================
# FRAUD ANALYSIS
# ============================================================

if analyze:

    result = predict_fraud(
        step=step,
        transaction_type=transaction_type,
        amount=amount,
        oldbalanceOrg=oldbalanceOrg,
        newbalanceOrig=newbalanceOrig,
        oldbalanceDest=oldbalanceDest,
        newbalanceDest=newbalanceDest,
        threshold=threshold
    )

    probability = result["fraud_probability"]
    fraud_percentage = result["fraud_percentage"]
    risk_level = result["risk_level"]
    decision = result["decision"]

    confidence = get_confidence(probability)

    risk_color = get_risk_color(risk_level)


    st.divider()


    # ========================================================
    # RESULT HEADER
    # ========================================================

    st.markdown(
        '<div class="section-title">Fraud Analysis Result</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # SUMMARY CARDS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="card">
                <div class="card-label">FRAUD SCORE</div>
                <div class="card-value {risk_color}">
                    {fraud_percentage}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f"""
            <div class="card">
                <div class="card-label">RISK LEVEL</div>
                <div class="card-value {risk_color}">
                    {risk_level}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            f"""
            <div class="card">
                <div class="card-label">RECOMMENDATION</div>
                <div class="card-value {risk_color}">
                    {decision}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col4:

        st.markdown(
            f"""
            <div class="card">
                <div class="card-label">PREDICTION CONFIDENCE</div>
                <div class="card-value">
                    {get_confidence(probability)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # FRAUD PROBABILITY BAR
    # ========================================================

    st.markdown("### Fraud Risk Score")

    st.progress(
        min(max(float(probability), 0.0), 1.0)
    )

    st.caption(
        f"Model-estimated fraud probability: {fraud_percentage}% | "
        f"Decision threshold: {threshold}"
    )


    st.divider()


    # ========================================================
    # TRANSACTION SUMMARY + INDICATORS
    # ========================================================

    summary_col, indicator_col = st.columns(2)


    # ---------------- TRANSACTION SUMMARY ----------------

    with summary_col:

        st.markdown("### 📄 Transaction Summary")

        summary_data = {
            "Transaction Type": transaction_type,
            "Transaction Step": step,
            "Transaction Amount": f"₹{amount:,.2f}",
            "Sender Balance": (
                f"₹{oldbalanceOrg:,.2f} → "
                f"₹{newbalanceOrig:,.2f}"
            ),
            "Receiver Balance": (
                f"₹{oldbalanceDest:,.2f} → "
                f"₹{newbalanceDest:,.2f}"
            ),
            "Detection Threshold": threshold
        }

        for label, value in summary_data.items():

            st.markdown(
                f"""
                <div class="indicator-card">
                    <b>{label}</b><br>
                    {value}
                </div>
                """,
                unsafe_allow_html=True
            )


    # ---------------- FRAUD INDICATORS ----------------

    with indicator_col:

        st.markdown("### ⚠️ Detected Risk Indicators")

        indicators = get_fraud_indicators(
            transaction_type,
            amount,
            oldbalanceOrg,
            newbalanceOrig,
            oldbalanceDest,
            newbalanceDest
        )

        if indicators:

            for indicator in indicators:

                st.markdown(
                    f"""
                    <div class="indicator-card">
                        {indicator}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.success(
                "No major rule-based risk indicators were detected."
            )


    st.divider()


    # ========================================================
    # FINAL RECOMMENDATION
    # ========================================================

    st.markdown("### 🛡️ System Recommendation")


    if risk_level == "CRITICAL":

        st.error(
            "🚨 BLOCK TRANSACTION — High probability of fraud detected. "
            "Flag this transaction for immediate investigation."
        )

    elif risk_level == "HIGH":

        st.warning(
            "🚨 HIGH RISK — Hold the transaction and send it for "
            "manual fraud review."
        )

    elif risk_level == "MEDIUM":

        st.info(
            "🔍 MEDIUM RISK — Allow only after additional verification "
            "or enhanced monitoring."
        )

    else:

        st.success(
            "✅ LOW RISK — No significant fraud risk detected. "
            "Transaction can proceed."
        )


    # ========================================================
    # TECHNICAL DETAILS
    # ========================================================

    with st.expander("🔧 View Technical Prediction Details"):

        st.json(result)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "FraudShield • Machine Learning Powered Financial Fraud Detection System"
)