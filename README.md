# 🛡️ FraudShield

An end-to-end AI-powered financial fraud detection and risk intelligence system.

FraudShield uses a machine learning model to analyze financial transactions and predict the probability of fraud. The system provides risk classification, transaction decisions, risk factors, fraud alerts, analytics, and an interactive dashboard.

---

## 🚀 Features

- 🤖 Machine Learning-based fraud detection
- 📊 Fraud probability and fraud score prediction
- 🚨 Risk classification
  - LOW
  - MEDIUM
  - HIGH
  - CRITICAL
- 🧠 Risk factor generation
- 🛑 Transaction decision recommendations
  - ALLOW TRANSACTION
  - MONITOR TRANSACTION
  - FLAG FOR REVIEW
  - BLOCK TRANSACTION
- 📈 Transaction analytics dashboard
- 🚨 Fraud alert management
- 📝 Analyst notes for fraud alerts
- 🔄 Alert status management
- 📋 Recent transaction monitoring
- 🌐 REST API built with FastAPI
- ⚛️ Interactive frontend built with React and Vite
- 💾 Transaction and alert storage using SQLite

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │   React + Vite UI   │
                    │     Dashboard       │
                    └──────────┬──────────┘
                               │
                               │ HTTP Requests
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    │      REST API       │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
      │ ML Prediction│  │  Analytics   │  │ Fraud Alerts │
      │    Service   │  │    Service   │  │  Management  │
      └──────┬───────┘  └──────────────┘  └──────────────┘
             │
             ▼
      ┌──────────────┐
      │ XGBoost Model│
      │ + Preprocessor│
      └──────────────┘
             │
             ▼
      ┌──────────────────────┐
      │   SQLite Database    │
      │ Transactions & Alerts│
      └──────────────────────┘
```

---

# 🧠 Machine Learning Pipeline

The fraud detection pipeline follows these steps:

```text
Transaction Input
       │
       ▼
Feature Engineering
       │
       ▼
Data Preprocessing
       │
       ▼
XGBoost Fraud Detection Model
       │
       ▼
Fraud Probability
       │
       ▼
Risk Classification
       │
       ├── LOW
       ├── MEDIUM
       ├── HIGH
       └── CRITICAL
       │
       ▼
Transaction Decision + Risk Factors
```

---

# 📊 Input Features

The model analyzes transaction information such as:

- Transaction step
- Transaction type
- Transaction amount
- Sender's old balance
- Sender's new balance
- Receiver's old balance
- Receiver's new balance

Additional engineered features include:

- Sender balance error
- Receiver balance error
- Origin account empty after transaction
- Destination account empty before transaction
- Amount-to-origin-balance ratio

---

# ⚙️ Tech Stack

## Machine Learning

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Joblib

## Backend

- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

## Frontend

- React
- Vite
- JavaScript
- CSS

## Database

- SQLite

---

# 📁 Project Structure

```text
fraudshield/
│
├── backend/
│   ├── api/
│   │   ├── transactions.py
│   │   ├── alerts.py
│   │   └── analytics.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │   └── transaction.py
│   │
│   ├── services/
│   │   └── prediction_service.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── models/
│   ├── xgboost_fraud_model.joblib
│   └── preprocessor.joblib
│
├── src/
│   └── predict.py
│
├── data/
├── notebooks/
│
├── requirements.txt
├── test_prediction.py
├── .gitignore
└── README.md
```

---

# 🔌 API Endpoints

## Analyze Transaction

```http
POST /transactions/analyze
```

Example request:

```json
{
  "step": 10,
  "transaction_type": "TRANSFER",
  "amount": 50000,
  "oldbalanceOrg": 50000,
  "newbalanceOrig": 0,
  "oldbalanceDest": 0,
  "newbalanceDest": 50000
}
```

The API returns information including:

- Transaction ID
- Fraud probability
- Fraud score
- Fraud prediction
- Risk level
- Recommended decision
- Risk factors

---

## Get All Transactions

```http
GET /transactions/
```

Returns the stored transaction history.

---

## Get Transaction by ID

```http
GET /transactions/{transaction_id}
```

---

## Fraud Alerts

```http
GET /alerts/
```

Retrieve fraud alerts generated for suspicious transactions.

The application also supports alert status management and analyst notes.

---

## Analytics Summary

```http
GET /analytics/summary
```

Provides dashboard analytics such as:

- Total transactions
- Fraud transactions
- Fraud rate
- Open alerts

---

# 🖥️ Running the Project Locally

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd fraudshield
```

---

## 2. Create and activate a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Start the FastAPI backend

From the root project folder:

```bash
uvicorn backend.main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 5. Configure the frontend

Go to the frontend folder:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create a `.env` file:

```env
VITE_API_URL=http://127.0.0.1:8000
```

---

## 6. Start the frontend

```bash
npm run dev
```

Open the URL displayed by Vite, usually:

```text
http://localhost:5173
```

---

# 📸 Application Workflow

1. Enter transaction details in the dashboard.
2. Submit the transaction for analysis.
3. The FastAPI backend sends the transaction to the ML prediction pipeline.
4. The XGBoost model calculates the fraud probability.
5. The system determines the fraud prediction and risk level.
6. Risk factors and a transaction decision are generated.
7. The transaction is stored in the database.
8. High-risk transactions generate fraud alerts.
9. The dashboard displays updated analytics, transactions, and alerts.

---

# 🎯 Project Purpose

FraudShield was built as an end-to-end machine learning application to demonstrate how a trained fraud detection model can be integrated into a complete software system.

The project combines:

- Machine Learning
- Feature Engineering
- Model Inference
- REST API Development
- Database Integration
- Frontend Development
- Fraud Alert Management
- Analytics Dashboard

---

# 🔮 Future Improvements

Possible future improvements include:

- PostgreSQL database for production persistence
- User authentication and role-based access
- Improved fraud classification for highly imbalanced data
- Advanced model monitoring
- Explainable AI integration
- Real-time transaction streaming
- Docker containerization
- Cloud deployment with persistent storage
- Automated model retraining pipeline

---

# 👨‍💻 Author

**Khush Hingrajiya**

AI/ML and Software Development Enthusiast

---

⭐ If you found this project interesting, consider giving the repository a star!