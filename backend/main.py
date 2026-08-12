"""
FastAPI backend for AI Side Effect Checker
Run: uvicorn backend.main:app --reload --port 8000
Neural Network (MLP) powered drug safety analysis.
"""

import os
import sys
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
ARTIFACTS = ROOT / "model" / "artifacts"
DATA = ROOT / "data" / "processed"

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Side Effect Checker API",
    description="Neural Network-powered drug safety analysis with clinical risk factor breakdown",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://itmed-safe-1fq77dxp8-adityaag5492045-6100s-projects.vercel.app",
        "https://medsafeai-iep6.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models & Data (loaded at startup) ────────────────────────────────────────
ml_model = None
scaler = None
label_encoder = None
metadata = None
drug_knowledge: Dict = {}
interactions_db: List = []
symptoms_mapping: Dict = {}

FEATURE_COLS = [
    "side_effect_count", "severity_score", "serious_event_rate",
    "interaction_count", "interaction_flag", "has_high_interaction"
]
RISK_LABELS = ["Low", "Medium", "High"]

@app.on_event("startup")
async def load_resources():
    global ml_model, scaler, label_encoder, metadata
    global drug_knowledge, interactions_db, symptoms_mapping

    print("[STARTUP] Loading ML model and data...")

    # Load model artifacts
    try:
        with open(ARTIFACTS / "model.pkl", "rb") as f:
            ml_model = pickle.load(f)
        with open(ARTIFACTS / "scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
        with open(ARTIFACTS / "label_encoder.pkl", "rb") as f:
            label_encoder = pickle.load(f)
        with open(ARTIFACTS / "metadata.json", encoding="utf-8") as f:
            metadata = json.load(f)
        print(f"[OK] ML Model loaded: {metadata.get('model_type', 'Unknown')}")
    except FileNotFoundError as e:
        print(f"[WARN] Model artifacts not found: {e}")
        print("   Run: python data/fetch_data.py && python model/train.py")

    # Load drug knowledge base
    try:
        with open(DATA / "drug_knowledge.json", encoding="utf-8") as f:
            drug_knowledge = json.load(f)
        print(f"[OK] Drug knowledge base: {len(drug_knowledge)} drugs")
    except FileNotFoundError:
        print("[WARN] drug_knowledge.json not found")

    # Load interactions
    try:
        with open(DATA / "interactions.json", encoding="utf-8") as f:
            interactions_db = json.load(f)
        print(f"[OK] Drug interactions: {len(interactions_db)} pairs")
    except FileNotFoundError:
        print("[WARN] interactions.json not found")
        
    # Load symptoms mapping
    try:
        with open(DATA / "symptoms_mapping.json", encoding="utf-8") as f:
            symptoms_mapping = json.load(f)
        print(f"[OK] Symptoms mapping loaded: {len(symptoms_mapping)} symptoms")
    except FileNotFoundError:
        print("[WARN] symptoms_mapping.json not found")

# ── Pydantic Schemas ──────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    drugs: List[str]


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    response: str


class ClinicalFactor(BaseModel):
    feature: str
    value: float
    impact: str
    contribution: float


class ClinicalFactors(BaseModel):
    top_factors: List[ClinicalFactor]
    explanation_text: str
    base_risk: str


class DrugResult(BaseModel):
    drug: str
    found_in_db: bool
    risk_level: str
    risk_score: float
    risk_color: str
    side_effects: List[str]
    severity_score: float
    serious_event_rate: float
    clinical_factors: Optional[ClinicalFactors]
    demographics: Optional[Dict[str, Any]] = None
    specialist_consult: Optional[str] = None
    clinical_consensus: Optional[str] = None


class Interaction(BaseModel):
    drug_a: str
    drug_b: str
    severity: str
    description: str
    severity_color: str
    evidence_level: Optional[str] = None
    verified_source: Optional[str] = None


class PredictResponse(BaseModel):
    results: List[DrugResult]
    interactions: List[Interaction]
    combined_risk: str
    combined_risk_color: str
    summary: str
    consultation_suggestion: str

# ── Helper Functions ──────────────────────────────────────────────────────────
def normalize_drug_name(name: str) -> str:
    return name.lower().strip()


def get_risk_color(risk: str) -> str:
    colors = {"Low": "#00C896", "Medium": "#FFB830", "High": "#FF4757"}
    return colors.get(risk, "#888")


def get_severity_color(severity: str) -> str:
    colors = {"Low": "#00C896", "Medium": "#FFB830", "High": "#FF4757"}
    return colors.get(severity, "#888")


def get_drug_features(drug_name: str) -> Dict:
    """Extract ML features for a given drug."""
    info = drug_knowledge.get(drug_name, {})
    se_list = info.get("side_effects", [])
    se_count = len(se_list) if se_list else 5
    severity = info.get("severity_score", 5.0) or 5.0
    serious = info.get("serious_event_rate", 0.05) or 0.05

    # Count interactions for this drug
    int_count = 0
    has_high = 0
    for inter in interactions_db:
        a = inter["drug_a"].lower()
        b = inter["drug_b"].lower()
        if a == drug_name or b == drug_name:
            int_count += 1
            if inter["severity"] == "High":
                has_high = 1

    int_flag = 1 if int_count > 0 else 0

    return {
        "side_effect_count": se_count,
        "severity_score": severity,
        "serious_event_rate": serious,
        "interaction_count": int_count,
        "interaction_flag": int_flag,
        "has_high_interaction": has_high,
    }


def predict_risk(features: Dict) -> Tuple[str, float]:
    """Run ML prediction and return (risk_label, risk_score)."""
    if ml_model is None:
        # Fallback rule-based prediction
        score = 0
        if features["severity_score"] >= 7.0:
            score += 3
        elif features["severity_score"] >= 5.0:
            score += 2
        else:
            score += 1
        if features["serious_event_rate"] >= 0.15:
            score += 3
        elif features["serious_event_rate"] >= 0.07:
            score += 2
        else:
            score += 1
        if features["has_high_interaction"]:
            score += 3
        elif features["interaction_count"] > 0:
            score += 1

        if score >= 6:
            return "High", 0.85
        elif score >= 4:
            return "Medium", 0.55
        else:
            return "Low", 0.20

    feat_array = np.array([[features[c] for c in FEATURE_COLS]])
    feat_scaled = scaler.transform(feat_array)
    pred_idx = ml_model.predict(feat_scaled)[0]
    proba = ml_model.predict_proba(feat_scaled)[0]

    risk_label = RISK_LABELS[pred_idx]
    risk_score = float(proba[pred_idx])
    return risk_label, risk_score


def get_clinical_factors(features: Dict, risk_label: str) -> ClinicalFactors:
    """Generate clinical factor breakdown for the prediction using rule-based heuristics."""
    factors = []
    feature_labels = {
        "side_effect_count": "Number of Side Effects",
        "severity_score": "Severity Score",
        "serious_event_rate": "Serious Adverse Event Rate",
        "interaction_count": "Drug Interaction Count",
        "interaction_flag": "Has Drug Interactions",
        "has_high_interaction": "Has High-Severity Interactions",
    }

    for col in FEATURE_COLS:
        val = features[col]
        # Rule-based contribution scoring
        if col == "severity_score":
            contribution = (val - 5.0) * 0.15
        elif col == "serious_event_rate":
            contribution = (val - 0.08) * 2.5
        elif col == "side_effect_count":
            contribution = (val - 6) * 0.05
        elif col == "has_high_interaction":
            contribution = val * 0.4
        elif col == "interaction_count":
            contribution = val * 0.1
        else:
            contribution = val * 0.05

        abs_contribution = abs(contribution)
        if abs_contribution >= 0.15:
            impact = "high"
        elif abs_contribution >= 0.06:
            impact = "medium"
        else:
            impact = "low"

        factors.append(ClinicalFactor(
            feature=feature_labels[col],
            value=round(val, 3),
            impact=impact,
            contribution=round(contribution, 4)
        ))

    factors.sort(key=lambda x: abs(x.contribution), reverse=True)
    top_factors = factors[:4]

    # Build human-readable explanation
    explanation_parts = []
    if features["has_high_interaction"]:
        explanation_parts.append("high-severity drug interactions")
    if features["serious_event_rate"] >= 0.15:
        explanation_parts.append(f"a high serious adverse event rate ({features['serious_event_rate']*100:.0f}%)")
    if features["severity_score"] >= 7.0:
        explanation_parts.append(f"a high severity score ({features['severity_score']:.1f}/10)")
    if features["side_effect_count"] >= 8:
        explanation_parts.append(f"{features['side_effect_count']} documented side effects")
    if features["interaction_count"] >= 3:
        explanation_parts.append(f"{features['interaction_count']} known drug interactions")

    if explanation_parts:
        text = f"Risk assessed as **{risk_label}** based on: {', '.join(explanation_parts[:3])}."
    else:
        if risk_label == "Low":
            text = "Low risk: minimal side effects, no severe interactions, and low adverse event rate."
        elif risk_label == "Medium":
            text = "Moderate risk: some notable side effects or potential interactions require attention."
        else:
            text = "High risk: significant adverse effects, dangerous interactions, or high serious event rate."

    base_map = {
        "Low": "Generally safe with standard monitoring",
        "Medium": "Use with caution — consult healthcare provider",
        "High": "High-risk medication — medical supervision required"
    }

    return ClinicalFactors(
        top_factors=top_factors,
        explanation_text=text,
        base_risk=base_map[risk_label]
    )


def find_interactions(drug_list: List[str]) -> List[Interaction]:
    """Find interactions between all provided drugs."""
    found = []
    for i in range(len(drug_list)):
        for j in range(i + 1, len(drug_list)):
            a = drug_list[i]
            b = drug_list[j]
            for inter in interactions_db:
                ia = inter["drug_a"].lower()
                ib = inter["drug_b"].lower()
                if (ia == a and ib == b) or (ia == b and ib == a):
                    found.append(Interaction(
                        drug_a=inter["drug_a"],
                        drug_b=inter["drug_b"],
                        severity=inter["severity"],
                        description=inter["description"],
                        severity_color=get_severity_color(inter["severity"]),
                        evidence_level=inter.get("evidence_level"),
                        verified_source=inter.get("verified_source")
                    ))
    return found


def compute_combined_risk(results: List[DrugResult], interactions: List[Interaction]) -> str:
    """Compute aggregate risk across all drugs and interactions."""
    risk_scores = {"Low": 1, "Medium": 2, "High": 3}
    individual_max = max((risk_scores.get(r.risk_level, 1) for r in results), default=1)

    has_high_interaction = any(i.severity == "High" for i in interactions)
    has_med_interaction = any(i.severity == "Medium" for i in interactions)

    combined_score = individual_max
    if has_high_interaction:
        combined_score = max(combined_score, 3)
    elif has_med_interaction:
        combined_score = max(combined_score, 2)

    # Extra penalty for 3+ drugs
    if len(results) >= 3:
        combined_score = min(combined_score + 1, 3)

    return {1: "Low", 2: "Medium", 3: "High"}.get(combined_score, "Medium")


# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": ml_model is not None,
        "model_type": metadata.get("model_type", "Unknown") if metadata else "Unknown",
        "drugs_in_db": len(drug_knowledge),
        "interactions_in_db": len(interactions_db)
    }


@app.get("/search")
async def search_drugs(q: str = Query(..., min_length=1)):
    """Autocomplete drug name search."""
    query = q.lower()
    matches = [
        drug for drug in drug_knowledge.keys()
        if query in drug.lower() and not drug.startswith("synthetic_")
    ]
    matches.sort(key=lambda x: (not x.lower().startswith(query), len(x)))
    return {"suggestions": matches[:15], "query": q}


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """Predict risk for one or more drugs with clinical factor analysis."""
    if not request.drugs:
        raise HTTPException(status_code=400, detail="At least one drug name required")

    normalized = [normalize_drug_name(d) for d in request.drugs]

    results = []
    for drug in normalized:
        found = drug in drug_knowledge
        features = get_drug_features(drug)
        risk_label, risk_score = predict_risk(features)
        clinical = get_clinical_factors(features, risk_label)

        info = drug_knowledge.get(drug, {})
        side_effects = info.get("side_effects", [])
        if not side_effects:
            if risk_label == "High":
                side_effects = ["Consult a doctor before use", "May cause serious adverse events", "Monitor closely for side effects"]
            elif risk_label == "Medium":
                side_effects = ["Mild to moderate side effects possible", "Follow dosage instructions carefully"]
            else:
                side_effects = ["Generally well-tolerated", "Mild side effects may occur"]

        results.append(DrugResult(
            drug=drug,
            found_in_db=found,
            risk_level=risk_label,
            risk_score=round(risk_score, 3),
            risk_color=get_risk_color(risk_label),
            side_effects=side_effects,
            severity_score=round(features["severity_score"], 1),
            serious_event_rate=round(features["serious_event_rate"], 3),
            clinical_factors=clinical,
            demographics=info.get("demographics"),
            specialist_consult=info.get("specialist_consult"),
            clinical_consensus=info.get("clinical_consensus")
        ))

    interactions = find_interactions(normalized)
    combined_risk = compute_combined_risk(results, interactions)

    # Build summary and consultation suggestions
    drug_names = ", ".join(d.drug.title() for d in results)
    if len(interactions) > 0:
        int_str = f"{len(interactions)} drug interaction(s) detected."
    else:
        int_str = "No drug interactions detected."
    
    summary = f"Analysis of {drug_names}: Overall risk is **{combined_risk}**. {int_str}"
    
    if combined_risk == "High":
        consultation = "⚠️ HIGH RISK: Immediate doctor consultation is strongly recommended. Do not start, stop, or change these medications without medical supervision. The predicted risk profile suggests potential for severe adverse events or dangerous drug interactions."
    elif combined_risk == "Medium":
        consultation = "ℹ️ MODERATE RISK: Please discuss these medications with your pharmacist or doctor during your next visit. Monitor closely for any of the listed side effects, especially when starting a new prescription."
    else:
        consultation = "✅ LOW RISK: These medications generally have a favorable safety profile. Standard monitoring applies. Always follow the prescribed dosage and consult a healthcare provider if you experience unexpected symptoms."

    return PredictResponse(
        results=results,
        interactions=interactions,
        combined_risk=combined_risk,
        combined_risk_color=get_risk_color(combined_risk),
        summary=summary,
        consultation_suggestion=consultation
    )


@app.get("/drug/{name}")
async def get_drug_info(name: str):
    """Get full information for a specific drug."""
    drug = normalize_drug_name(name)
    if drug not in drug_knowledge:
        raise HTTPException(status_code=404, detail=f"Drug '{name}' not found in database")

    info = drug_knowledge[drug]
    return {
        "drug": drug,
        "side_effects": info.get("side_effects", []),
        "severity_score": info.get("severity_score"),
        "serious_event_rate": info.get("serious_event_rate"),
        "interactions": info.get("interactions", [])
    }


@app.get("/symptoms/search")
async def search_by_symptom(q: str = Query(..., min_length=2)):
    """Search for drugs based on symptoms."""
    query = q.lower().strip()
    
    # Try exact match first
    if query in symptoms_mapping:
        return symptoms_mapping[query]
        
    # Partial match
    matches = []
    for symptom, data in symptoms_mapping.items():
        if query in symptom:
            matches.append({"symptom": symptom, **data})
            
    if matches:
        # Return the best match
        return matches[0]
        
    raise HTTPException(status_code=404, detail=f"No medications found for symptom '{q}'. Please try another symptom like 'headache', 'fever', or 'pain'.")


@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    """Handle customer interactions via chatbot."""
    msg = request.message.lower().strip()
    
    # Basic rule-based chatbot logic
    if re.search(r"hello|hi|hey|help", msg):
        return ChatResponse(response="Hello! I'm the MedSafe AI assistant. I can help you understand medicine side effects, check for interactions, or find medicines for specific symptoms. What can I help you with today?")
        
    if re.search(r"what is (\w+)", msg):
        match = re.search(r"what is ([\w\s]+)", msg)
        if match:
            drug = normalize_drug_name(match.group(1).split("?")[0].strip())
            if drug in drug_knowledge:
                se = ", ".join(drug_knowledge[drug].get("side_effects", [])[:3])
                return ChatResponse(response=f"{drug.title()} is a medication in our database. Some common side effects include: {se}. Would you like me to analyze its safety profile?")
    
    if re.search(r"headache|fever|pain|allergies|cough|nausea", msg):
        return ChatResponse(response="It sounds like you're experiencing some symptoms. I recommend using the 'Search by Symptom' feature on our main page to get specific medication recommendations and doctor consultation advice.")
        
    if "interaction" in msg or "safe" in msg:
        return ChatResponse(response="To check if medications are safe to take together, please enter them in the analysis tool on the main page. I'll use our AI model to check for interactions and predict the overall risk.")
        
    # Fallback response
    return ChatResponse(response="I'm a medical AI assistant. You can ask me about specific medicines, symptoms, or use our main tool to analyze drug interactions. Always consult a real doctor for medical advice.")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server on http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
