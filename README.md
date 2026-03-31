# AI Side Effect Checker for Medicines 💊🤖

A full-stack, hackathon-level web application that predicts medication risk, highlights drug interactions, and uses Explainable AI (SHAP) to tell you *why* a particular medicine is risky.

## Tech Stack
* **Frontend**: React, Vite, Framer Motion, TypeScript
* **Backend**: FastAPI, Python, Uvicorn
* **Machine Learning**: XGBoost, SHAP (Explainable AI), Scikit-Learn
* **Data Sources**: SIDER (Side Effect Resource), OpenFDA, Curated Interaction Datasets

---

## 🚀 How to Run the Project

### Prerequisites
Make sure you have both **Python 3.9+** and **Node.js 18+** installed.

### 1. Generate Data & Train the ML Model
First, run the data pipeline to build the synthetic and curated databases, then train the XGBoost model.

```bash
cd backend

# (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux

# Install backend ML and API dependencies
pip install -r requirements.txt
```

Run the data pipeline and model training from the project root:
```bash
# 1. Fetch data and build the features CSV and Knowledge base JSON
python data/fetch_data.py

# 2. Train the XGBoost model and generate the SHAP explainer
python model/train.py
```
*(This will generate artifacts like `model.pkl`, `scaler.pkl`, and `shap_explainer.pkl` in the `model/artifacts/` folder).*

---

### 2. Start the FastAPI Backend
The backend serves the ML model predictions and drug autocomplete searches via a REST API.

```bash
# Start the Uvicorn server (make sure you are in the project root, or set PYTHONPATH pointing to it)
python -m uvicorn backend.main:app --reload --port 8000
```
*The backend API will be available at: [http://localhost:8000](http://localhost:8000)*
*Interactive API Documentation (SwaggerUI): [http://localhost:8000/docs](http://localhost:8000/docs)*

---

### 3. Start the React Frontend
In a new terminal window, start the React development server.

```bash
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```
*The frontend web application will be available at: [http://localhost:5173](http://localhost:5173)*

---

### Architecture Overview
1. **Frontend**: The user searches for one or more medicines using a debounced autocomplete input. Clicking "Analyze Risk" sends a POST request with the selected drugs to the backend.
2. **Backend Engine**: FastAPI intercepts the list, retrieves side-effect metrics (severity, frequency) and runs interaction checks for each drug pair against the internal SQLite/JSON DB. 
3. **ML Inference**: An XGBoost Classifier predicts the risk category (`Low`, `Medium`, or `High`).
4. **SHAP Explainability**: The SHAP `Explainer` extracts local feature importance values for the individual prediction, transforming the black-box model into a human-readable list of contributing risk factors.
5. **UI Rendering**: The React frontend visualizes the results using an animated SVG Risk Gauge, interactively mapped SHAP summary bars, and categorized interaction severity alerts.
