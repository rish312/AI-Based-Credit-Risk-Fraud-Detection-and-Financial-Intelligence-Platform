# ML Prediction Platform

A full-stack Machine Learning platform that scores customers and transactions across three independent models simultaneously: **Credit Risk**, **Fraud Detection**, and **Customer Segmentation**. 

The system explains every prediction using **SHAP (SHapley Additive exPlanations)** and surfaces the results through a unified REST API and a modern React web dashboard.

---

## 🚀 Features

* **Multi-Model ML Engine**: Evaluates three distinct machine learning models in parallel using `asyncio` with strict timeout controls and graceful fallbacks.
* **SHAP Explainability**: Integrates `TreeExplainer` and `KernelExplainer` to provide feature-level contribution analysis for every prediction.
* **Robust REST API**: Built with FastAPI, featuring:
  * JWT-based Authentication & Role-Based Access Control (RBAC)
  * Endpoint Rate Limiting (via `slowapi`)
  * Comprehensive Audit Logging middleware
* **Fraud Review Queue**: A dedicated workflow for transactions flagged as "manual review" by the fraud model.
* **Monitoring & Observability**: Real-time score distributions, latency metrics, and simulated drift alerts.
* **Modern Dashboard**: Built with React, Vite, and Tailwind CSS v4, visualizing complex ML outputs (like SHAP waterfall charts) intuitively.

---

## 🛠 Tech Stack

**Backend**
* Python 3.14+
* FastAPI (REST API & orchestration)
* Scikit-Learn, XGBoost / HistGradientBoosting (ML Models)
* SHAP (Model Explainability)
* SQLite (Persistence for users, audit logs, predictions, and queues)

**Frontend**
* React 18 & Vite
* Tailwind CSS v4 (Styling)
* Recharts (Data visualization)
* React Router v6 (Routing)

---

## 📂 Project Structure

```text
credit_riskml/
├── backend/
│   ├── api/             # FastAPI routers, schemas, and middleware (auth, audit, rate limit)
│   ├── ml/              # ML Engine, Feature Store, SHAP explainers
│   │   ├── credit_risk/ # Credit risk model, data generator, training script
│   │   ├── fraud/       # Fraud model, data generator, training script
│   │   └── segmentation/# Segmentation model, data generator, training script
│   ├── models/          # Serialized model artifacts (.joblib, metadata.json)
│   ├── config.py        # Environment variables & constants
│   ├── database.py      # SQLite schema and connections
│   └── main.py          # FastAPI application entry point
├── frontend/
│   ├── src/             # React components, pages, context, API client
│   ├── package.json     # Node dependencies
│   └── vite.config.js   # Vite configuration
├── scripts/             # Utilities for seeding users, generating demo data, and training
└── tests/               # Pytest suite
```

---

## ⚙️ Local Setup Instructions

### 1. Backend Setup

Open a terminal and navigate to the project root:

```bash
# Navigate to the project
cd credit_riskml

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Prepare the Database & ML Models

Train the models and populate the SQLite database with seed users and demo predictions:

```bash
# Train all three ML models from scratch
PYTHONPATH=. .venv/bin/python scripts/train_all.py

# Create the database schema and seed default users
PYTHONPATH=. .venv/bin/python scripts/seed_users.py

# Generate 30 synthetic predictions for the dashboard to display
PYTHONPATH=. .venv/bin/python scripts/generate_demo_data.py 30
```

### 3. Start the Services

**Start the FastAPI Backend:**
```bash
# From the project root
PYTHONPATH=. .venv/bin/uvicorn backend.main:app --reload --port 8000
```
*The API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs)*

**Start the React Frontend:**
Open a *new* terminal tab:
```bash
cd credit_riskml/frontend
npm install
npm run dev
```
*The dashboard will be available at [http://localhost:5173](http://localhost:5173)*

---

## 🔐 Default User Roles & Credentials

The `seed_users.py` script provisions the following accounts. Use these to log into the web dashboard:

| Role | Username | Password | Dashboard Access |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Full Access |
| **Loan Officer** | `loan_officer` | `loan123` | Predictions & Dashboard |
| **Fraud Analyst** | `fraud_analyst` | `fraud123` | Review Queue & Dashboard |
| **Compliance** | `compliance` | `comp123` | Monitoring & Audit Logs |
| **Viewer** | `viewer` | `viewer123` | Read-only Dashboard |

---

## 🧠 ML Models Overview

1. **Credit Risk Model**: Predicts the probability of default using a calibrated Gradient Boosting Classifier. Outputs a risk tier (Low, Medium, High, Very High) and a simulated credit score.
2. **Fraud Detection Model**: An ensemble model combining Gradient Boosting (for known fraud patterns) and Isolation Forest (for anomaly detection). Classifies transactions into `auto_approve`, `manual_review`, or `auto_decline`.
3. **Customer Segmentation Model**: Uses K-Means clustering to group customers (e.g., High-Value Loyalist, At-Risk Churner) and a Random Forest surrogate model to classify new users in real-time.

---

## 📄 License

This project is licensed under the MIT License.
