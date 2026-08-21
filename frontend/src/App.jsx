import { useEffect, useState } from "react";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

function App() {
  // ================= STATE =================

  const [transactions, setTransactions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    step: 1,
    transaction_type: "TRANSFER",
    amount: 50000,
    oldbalanceOrg: 100000,
    newbalanceOrig: 50000,
    oldbalanceDest: 0,
    newbalanceDest: 50000,
  });

  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  // ================= LOAD DASHBOARD DATA =================

  const loadData = async () => {
    try {
      setError("");

      const [
        transactionsRes,
        alertsRes,
        analyticsRes,
      ] = await Promise.all([
        fetch(`${API_URL}/transactions/`),
        fetch(`${API_URL}/alerts/`),
        fetch(`${API_URL}/analytics/summary`),
      ]);

      if (
        !transactionsRes.ok ||
        !alertsRes.ok ||
        !analyticsRes.ok
      ) {
        throw new Error(
          "Failed to connect to FraudShield backend."
        );
      }

      const transactionsData =
        await transactionsRes.json();

      const alertsData =
        await alertsRes.json();

      const analyticsData =
        await analyticsRes.json();

      setTransactions(transactionsData);
      setAlerts(alertsData);
      setAnalytics(analyticsData);

    } catch (err) {
      console.error(err);

      setError(
        "Failed to connect to FraudShield backend."
      );
    }
  };

  // ================= LOAD ON START =================

  useEffect(() => {
    loadData();
  }, []);

  // ================= FORM CHANGE =================

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData({
      ...formData,

      [name]:
        name === "transaction_type"
          ? value
          : Number(value),
    });
  };

  // ================= ANALYZE TRANSACTION =================

  const analyzeTransaction = async (e) => {
    e.preventDefault();

    try {
      setAnalyzing(true);
      setError("");
      setResult(null);

      const response = await fetch(
        `${API_URL}/transactions/analyze`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify(formData),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(
          errorData.detail ||
          "Transaction analysis failed."
        );
      }

      const data = await response.json();

      console.log(
        "Analyze API Response:",
        data
      );

      // ================= SAVE COMPLETE RESULT =================

      setResult({
        transaction_id:
          data.transaction_id ??
          data.id ??
          data.transaction?.id ??
          "N/A",

        is_fraud:
          data.is_fraud ??
          data.prediction ??
          data.fraud_prediction ??
          data.transaction?.is_fraud ??
          false,

        fraud_probability:
          data.fraud_probability ??
          data.transaction?.fraud_probability ??
          0,

        fraud_score:
          data.fraud_score ??
          data.fraud_percentage ??
          (
            data.fraud_probability !== undefined
              ? Number(data.fraud_probability) * 100
              : 0
          ),

        risk_level:
          data.risk_level ??
          data.risk ??
          data.transaction?.risk_level ??
          "LOW",

        decision:
          data.decision ??
          data.transaction?.decision ??
          "ALLOW TRANSACTION",

        risk_factors:
          data.risk_factors ??
          data.transaction?.risk_factors ??
          [],
      });

      // Refresh dashboard
      await loadData();

    } catch (err) {
      console.error(err);

      setError(
        err.message ||
        "Failed to analyze transaction."
      );

    } finally {
      setAnalyzing(false);
    }
  };

  // ================= UPDATE ALERT STATUS =================

  const updateAlertStatus = async (
    alertId,
    status
  ) => {
    try {
      setError("");

      const response = await fetch(
        `${API_URL}/alerts/${alertId}/status?status=${status}`,
        {
          method: "PATCH",
        }
      );

      if (!response.ok) {
        throw new Error(
          "Failed to update alert status."
        );
      }

      await loadData();

    } catch (err) {
      console.error(err);

      setError(
        "Failed to update alert status."
      );
    }
  };

  // ================= UPDATE ALERT NOTES =================

  const updateNotes = async (
    alertId,
    notes
  ) => {
    try {
      setError("");

      const response = await fetch(
        `${API_URL}/alerts/${alertId}/notes?notes=${encodeURIComponent(
          notes
        )}`,
        {
          method: "PATCH",
        }
      );

      if (!response.ok) {
        throw new Error(
          "Failed to save notes."
        );
      }

      await loadData();

    } catch (err) {
      console.error(err);

      setError(
        "Failed to save notes."
      );
    }
  };

  // ================= UI =================

  return (
    <div className="app">

      {/* ================= HEADER ================= */}

      <header className="header">
        <div>
          <h1>🛡️ FraudShield</h1>

          <p>
            AI-Powered Fraud Detection & Risk Intelligence
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          System Online
        </div>
      </header>


      {/* ================= DASHBOARD ================= */}

      <main className="dashboard">

        <div className="dashboard-header">
          <div>
            <h2>Dashboard</h2>

            <p>
              Monitor transactions, fraud risks, and alerts.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={loadData}
          >
            Refresh
          </button>
        </div>


        {/* ================= ERROR ================= */}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}


        {/* ================= ANALYZE PANEL ================= */}

        <div className="analyze-panel">

          <h3>
            Analyze New Transaction
          </h3>

          <form
            className="transaction-form"
            onSubmit={analyzeTransaction}
          >

            {/* STEP */}

            <div className="form-group">
              <label>Step</label>

              <input
                type="number"
                name="step"
                value={formData.step}
                onChange={handleChange}
                placeholder="Step"
                required
              />
            </div>


            {/* TRANSACTION TYPE */}

            <div className="form-group">
              <label>
                Transaction Type
              </label>

              <select
                name="transaction_type"
                value={formData.transaction_type}
                onChange={handleChange}
              >
                <option value="TRANSFER">
                  TRANSFER
                </option>

                <option value="PAYMENT">
                  PAYMENT
                </option>

                <option value="CASH_OUT">
                  CASH_OUT
                </option>

                <option value="DEBIT">
                  DEBIT
                </option>

                <option value="CASH_IN">
                  CASH_IN
                </option>
              </select>
            </div>


            {/* AMOUNT */}

            <div className="form-group">
              <label>Amount</label>

              <input
                type="number"
                name="amount"
                value={formData.amount}
                onChange={handleChange}
                placeholder="Amount"
                required
              />
            </div>


            {/* OLD SENDER BALANCE */}

            <div className="form-group">
              <label>
                Old Sender Balance
              </label>

              <input
                type="number"
                name="oldbalanceOrg"
                value={formData.oldbalanceOrg}
                onChange={handleChange}
                placeholder="Old Sender Balance"
                required
              />
            </div>


            {/* NEW SENDER BALANCE */}

            <div className="form-group">
              <label>
                New Sender Balance
              </label>

              <input
                type="number"
                name="newbalanceOrig"
                value={formData.newbalanceOrig}
                onChange={handleChange}
                placeholder="New Sender Balance"
                required
              />
            </div>


            {/* OLD RECEIVER BALANCE */}

            <div className="form-group">
              <label>
                Old Receiver Balance
              </label>

              <input
                type="number"
                name="oldbalanceDest"
                value={formData.oldbalanceDest}
                onChange={handleChange}
                placeholder="Old Receiver Balance"
                required
              />
            </div>


            {/* NEW RECEIVER BALANCE */}

            <div className="form-group">
              <label>
                New Receiver Balance
              </label>

              <input
                type="number"
                name="newbalanceDest"
                value={formData.newbalanceDest}
                onChange={handleChange}
                placeholder="New Receiver Balance"
                required
              />
            </div>


            {/* ANALYZE BUTTON */}

            <div className="form-group button-group">
              <label>&nbsp;</label>

              <button
                type="submit"
                className="analyze-button"
                disabled={analyzing}
              >
                {analyzing
                  ? "Analyzing..."
                  : "Analyze Transaction"}
              </button>
            </div>

          </form>


          {/* ================= ANALYSIS RESULT ================= */}

          {result && (
            <div className="analysis-result">

              <h3>Analysis Result</h3>

              <div className="analysis-grid">

                {/* TRANSACTION ID */}

                <div className="analysis-card">
                  <span>Transaction ID</span>

                  <strong>
                    #{result.transaction_id}
                  </strong>
                </div>


                {/* FRAUD PREDICTION */}

                <div className="analysis-card">
                  <span>
                    Fraud Prediction
                  </span>

                  <strong
                    className={
                      result.is_fraud
                        ? "fraud-text"
                        : "safe-text"
                    }
                  >
                    {result.is_fraud
                      ? "FRAUD"
                      : "NOT FRAUD"}
                  </strong>
                </div>


                {/* FRAUD SCORE */}

                <div className="analysis-card">
                  <span>
                    Fraud Score
                  </span>

                  <strong>
                    {Number(
                      result.fraud_score
                    ).toFixed(2)}%
                  </strong>
                </div>


                {/* RISK LEVEL */}

                <div className="analysis-card">
                  <span>
                    Risk Level
                  </span>

                  <strong
                    className={`risk-${String(
                      result.risk_level
                    ).toLowerCase()}`}
                  >
                    {result.risk_level}
                  </strong>
                </div>


                {/* DECISION */}

                <div className="analysis-card">
                  <span>
                    Decision
                  </span>

                  <strong>
                    {result.decision}
                  </strong>
                </div>

              </div>


              {/* ================= RISK FACTORS ================= */}

              <div className="risk-factors-section">

                <h4>
                  Risk Factors
                </h4>

                {result.risk_factors &&
                result.risk_factors.length > 0 ? (

                  <ul className="risk-factors-list">

                    {result.risk_factors.map(
                      (factor, index) => (
                        <li key={index}>
                          {factor}
                        </li>
                      )
                    )}

                  </ul>

                ) : (

                  <p className="no-risk-factors">
                    No significant risk factors detected.
                  </p>

                )}

              </div>

            </div>
          )}

        </div>


        {/* ================= STATS ================= */}

        <div className="stats-grid">

          <div className="card">
            <p>Total Transactions</p>

            <h2>
              {analytics?.total_transactions ?? 0}
            </h2>
          </div>


          <div className="card">
            <p>Fraud Transactions</p>

            <h2>
              {analytics?.fraud_transactions ?? 0}
            </h2>
          </div>


          <div className="card">
            <p>Fraud Rate</p>

            <h2>
              {analytics?.fraud_rate ?? 0}%
            </h2>
          </div>


          <div className="card">
            <p>Open Alerts</p>

            <h2>
              {analytics?.alerts?.open ?? 0}
            </h2>
          </div>

        </div>


        {/* ================= TRANSACTIONS + ALERTS ================= */}

        <div className="content-grid">


          {/* ================= RECENT TRANSACTIONS ================= */}

          <div className="panel">

            <h3>
              Recent Transactions
            </h3>

            {transactions.length === 0 ? (

              <div className="empty-state">
                No transactions available yet.
              </div>

            ) : (

              transactions.map(
                (transaction) => (

                  <div
                    className="transaction-item"
                    key={transaction.id}
                  >

                    <div>
                      <strong>
                        {transaction.transaction_type}
                      </strong>

                      <p>
                        ₹{transaction.amount}
                      </p>
                    </div>


                    <span
                      className={`risk-badge ${String(
                        transaction.risk_level
                      ).toLowerCase()}`}
                    >
                      {transaction.risk_level}
                    </span>

                  </div>

                )
              )

            )}

          </div>


          {/* ================= FRAUD ALERTS ================= */}

          <div className="panel">

            <h3>
              Fraud Alerts
            </h3>

            {alerts.length === 0 ? (

              <div className="empty-state">
                No fraud alerts available.
              </div>

            ) : (

              alerts.map(
                (alert) => (

                  <AlertItem
                    key={alert.id}
                    alert={alert}
                    updateAlertStatus={
                      updateAlertStatus
                    }
                    updateNotes={
                      updateNotes
                    }
                  />

                )
              )

            )}

          </div>

        </div>

      </main>

    </div>
  );
}


// ============================================================
// ALERT COMPONENT
// ============================================================

function AlertItem({
  alert,
  updateAlertStatus,
  updateNotes,
}) {
  const [notes, setNotes] = useState(
    alert.analyst_notes || ""
  );

  const [saving, setSaving] =
    useState(false);


  const handleSaveNotes = async () => {
    try {
      setSaving(true);

      await updateNotes(
        alert.id,
        notes
      );

    } finally {
      setSaving(false);
    }
  };


  return (
    <div className="alert-item">

      <div className="alert-top">

        <div>
          <strong>
            Alert #{alert.id}
          </strong>

          <p>
            Transaction #{alert.transaction_id}
          </p>
        </div>


        <span
          className={`alert-status status-${alert.status.toLowerCase()}`}
        >
          {alert.status}
        </span>

      </div>


      {/* ALERT ACTIONS */}

      <div className="alert-actions">

        <button
          onClick={() =>
            updateAlertStatus(
              alert.id,
              "OPEN"
            )
          }
        >
          Open
        </button>


        <button
          onClick={() =>
            updateAlertStatus(
              alert.id,
              "INVESTIGATING"
            )
          }
        >
          Investigating
        </button>


        <button
          className="resolve-button"
          onClick={() =>
            updateAlertStatus(
              alert.id,
              "RESOLVED"
            )
          }
        >
          Resolve
        </button>

      </div>


      {/* NOTES */}

      <textarea
        className="alert-notes"
        value={notes}
        onChange={(e) =>
          setNotes(e.target.value)
        }
        placeholder="Add analyst notes..."
      />


      <button
        className="save-notes-button"
        onClick={handleSaveNotes}
        disabled={saving}
      >
        {saving
          ? "Saving..."
          : "Save Notes"}
      </button>

    </div>
  );
}


export default App;