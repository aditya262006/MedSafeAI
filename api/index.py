"""
MedSafeAI Backend - Vercel Serverless Function
Deployed as API route on same domain as frontend
"""

import os
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
ARTIFACTS = ROOT / "model" / "artifacts"
DATA = ROOT / "data" / "processed"

# ── Models & Data (loaded at startup) ────────────────────────────────────────
ml_model = None
scaler = None
label_encoder = None
shap_explainer = None
metadata = None
drug_knowledge: Dict = {}
interactions_db: List = []

FEATURE_COLS = [
    "side_effect_count", "severity_score", "serious_event_rate",
    "interaction_count", "interaction_flag", "has_high_interaction"
]
RISK_LABELS = ["Low", "Medium", "High"]


def load_resources():
    """Load ML model and data at startup."""
    global ml_model, scaler, label_encoder, shap_explainer, metadata
    global drug_knowledge, interactions_db

    print("[API] Loading ML model and data...")

    # Load model artifacts
    try:
        with open(ARTIFACTS / "model.pkl", "rb") as f:
            ml_model = pickle.load(f)
        with open(ARTIFACTS / "scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
        with open(ARTIFACTS / "label_encoder.pkl", "rb") as f:
            label_encoder = pickle.load(f)
        with open(ARTIFACTS / "metadata.json") as f:
            metadata = json.load(f)
        print(f"[API] ML Model loaded: {metadata.get('model_type', 'Unknown')}")

        if (ARTIFACTS / "shap_explainer.pkl").exists():
            with open(ARTIFACTS / "shap_explainer.pkl", "rb") as f:
                shap_explainer = pickle.load(f)
            print("[API] SHAP explainer loaded")
    except FileNotFoundError as e:
        print(f"[API] Model artifacts not found: {e}")

    # Load drug knowledge base
    try:
        with open(DATA / "drug_knowledge.json") as f:
            drug_knowledge = json.load(f)
        print(f"[API] Drug knowledge base: {len(drug_knowledge)} drugs")
    except FileNotFoundError:
        print("[API] drug_knowledge.json not found")

    # Load interactions
    try:
        with open(DATA / "interactions.json") as f:
            interactions_db = json.load(f)
        print(f"[API] Drug interactions: {len(interactions_db)} pairs")
    except FileNotFoundError:
        print("[API] interactions.json not found")


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


def get_shap_explanation(features: Dict, risk_label: str) -> Dict:
    """Generate SHAP-based explanation for the prediction."""
    feat_array = np.array([[features[c] for c in FEATURE_COLS]])

    # Compute feature contributions
    factors = []
    feature_labels = {
        "side_effect_count": "Number of Side Effects",
        "severity_score": "Severity Score",
        "serious_event_rate": "Serious Adverse Event Rate",
        "interaction_count": "Drug Interaction Count",
        "interaction_flag": "Has Drug Interactions",
        "has_high_interaction": "Has High-Severity Interactions",
    }

    for i, col in enumerate(FEATURE_COLS):
        val = features[col]
        # Heuristic fallback (no SHAP in serverless for performance)
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

        factors.append({
            "feature": feature_labels[col],
            "value": round(val, 3),
            "impact": impact,
            "contribution": round(contribution, 4)
        })

    factors.sort(key=lambda x: abs(x["contribution"]), reverse=True)
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
        text = f"Risk predicted as **{risk_label}** due to: {', '.join(explanation_parts[:3])}."
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

    return {
        "top_factors": top_factors,
        "explanation_text": text,
        "base_risk": base_map[risk_label]
    }


def find_interactions(drug_list: List[str]) -> List[Dict]:
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
                    found.append({
                        "drug_a": inter["drug_a"],
                        "drug_b": inter["drug_b"],
                        "severity": inter["severity"],
                        "description": inter["description"],
                        "severity_color": get_severity_color(inter["severity"])
                    })
    return found


def compute_combined_risk(results: List[Dict], interactions: List[Dict]) -> str:
    """Compute aggregate risk across all drugs and interactions."""
    risk_scores = {"Low": 1, "Medium": 2, "High": 3}
    individual_max = max((risk_scores.get(r["risk_level"], 1) for r in results), default=1)

    has_high_interaction = any(i["severity"] == "High" for i in interactions)
    has_med_interaction = any(i["severity"] == "Medium" for i in interactions)

    combined_score = individual_max
    if has_high_interaction:
        combined_score = max(combined_score, 3)
    elif has_med_interaction:
        combined_score = max(combined_score, 2)

    # Extra penalty for 3+ drugs
    if len(results) >= 3:
        combined_score = min(combined_score + 1, 3)

    return {1: "Low", 2: "Medium", 3: "High"}.get(combined_score, "Medium")


# ── API Handlers ───────────────────────────────────────────────────────────────
def handle_request(request):
    """Handle incoming HTTP request."""
    path = request.path
    method = request.method

    # CORS headers
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Accept, Origin",
    }

    # Handle CORS preflight
    if method == "OPTIONS":
        return ("", 204, headers)

    try:
        # Health check
        if path == "/api/health" or path == "/health":
            return (json.dumps({
                "status": "healthy",
                "model_loaded": ml_model is not None,
                "drugs_in_db": len(drug_knowledge),
                "interactions_in_db": len(interactions_db)
            }), 200, headers)

        # Search endpoint
        if path == "/api/search" or path == "/search":
            q = request.args.get("q", "").strip()
            if not q or len(q) < 1:
                return (json.dumps({"error": "Query parameter 'q' required"}), 400, headers)

            query = q.lower()
            matches = [
                drug for drug in drug_knowledge.keys()
                if query in drug.lower() and not drug.startswith("synthetic_")
            ]
            matches.sort(key=lambda x: (not x.lower().startswith(query), len(x)))
            return (json.dumps({"suggestions": matches[:15], "query": q}), 200, headers)

        # Predict endpoint
        if path == "/api/predict" or path == "/predict":
            if method != "POST":
                return (json.dumps({"error": "POST method required"}), 405, headers)

            try:
                data = request.json or {}
            except:
                data = {}

            if not data or "drugs" not in data:
                return (json.dumps({"error": "Request must contain 'drugs' list"}), 400, headers)

            drugs = data.get("drugs", [])
            if not isinstance(drugs, list):
                return (json.dumps({"error": "'drugs' must be a list"}), 400, headers)

            if not drugs:
                return (json.dumps({"error": "At least one drug name required"}), 400, headers)

            if len(drugs) > 10:
                return (json.dumps({"error": "Maximum 10 drugs per request"}), 400, headers)

            # Normalize drug names
            normalized = [normalize_drug_name(d) for d in drugs]

            results = []
            for drug in normalized:
                found = drug in drug_knowledge
                features = get_drug_features(drug)
                risk_label, risk_score = predict_risk(features)
                shap_exp = get_shap_explanation(features, risk_label)

                info = drug_knowledge.get(drug, {})
                side_effects = info.get("side_effects", [])
                if not side_effects:
                    if risk_label == "High":
                        side_effects = ["Consult a doctor before use", "May cause serious adverse events", "Monitor closely for side effects"]
                    elif risk_label == "Medium":
                        side_effects = ["Mild to moderate side effects possible", "Follow dosage instructions carefully"]
                    else:
                        side_effects = ["Generally well-tolerated", "Mild side effects may occur"]

                results.append({
                    "drug": drug,
                    "found_in_db": found,
                    "risk_level": risk_label,
                    "risk_score": round(risk_score, 3),
                    "risk_color": get_risk_color(risk_label),
                    "side_effects": side_effects,
                    "severity_score": round(features["severity_score"], 1),
                    "serious_event_rate": round(features["serious_event_rate"], 3),
                    "shap_explanation": shap_exp
                })

            interactions = find_interactions(normalized)
            combined_risk = compute_combined_risk(results, interactions)

            # Build summary
            drug_names = ", ".join(d["drug"].title() for d in results)
            int_str = f"{len(interactions)} drug interaction(s) detected." if interactions else "No drug interactions detected."
            summary = f"Analysis of {drug_names}: Overall risk is **{combined_risk}**. {int_str}"

            return (json.dumps({
                "results": results,
                "interactions": interactions,
                "combined_risk": combined_risk,
                "combined_risk_color": get_risk_color(combined_risk),
                "summary": summary
            }), 200, headers)

        # Drug info endpoint
        if path.startswith("/api/drug/") or path.startswith("/drug/"):
            name = path.split("/")[-1]
            drug = normalize_drug_name(name)
            if drug not in drug_knowledge:
                return (json.dumps({"error": f"Drug '{name}' not found in database"}), 404, headers)

            info = drug_knowledge[drug]
            return (json.dumps({
                "drug": drug,
                "side_effects": info.get("side_effects", []),
                "severity_score": info.get("severity_score"),
                "serious_event_rate": info.get("serious_event_rate"),
                "interactions": info.get("interactions", [])
            }), 200, headers)

        return (json.dumps({"error": "Endpoint not found"}), 404, headers)

    except Exception as e:
        print(f"[API] Error: {e}")
        return (json.dumps({"error": str(e)}), 500, headers)


# ── Vercel Handler ──────────────────────────────────────────────────────────────
class QueryParams:
    """Simple dict-like object for query parameters."""
    def __init__(self, params_dict):
        self.params = params_dict or {}
    
    def get(self, key, default=None):
        return self.params.get(key, default)


class VercelRequest:
    """Wrapper for Vercel event to look like a request object."""
    def __init__(self, event):
        self.path = event.get("path", "/")
        self.method = event.get("method", "GET").upper()
        self.headers = event.get("headers", {})
        self.body = event.get("body", "")
        
        # Query parameters from Vercel - already a dict
        query_params = event.get("queryStringParameters") or {}
        self.args = QueryParams(query_params)
        
        # Parse JSON body
        self._json = None
    
    @property
    def json(self):
        """Parse and cache JSON body."""
        if self._json is None:
            if self.body:
                try:
                    self._json = json.loads(self.body) if isinstance(self.body, str) else self.body
                except Exception as e:
                    print(f"[API] Failed to parse JSON body: {e}")
                    self._json = {}
            else:
                self._json = {}
        return self._json


# Try to load resources, but don't crash if it fails
try:
    print("[API] Initializing MedSafeAI backend...")
    load_resources()
    print("[API] Backend initialized successfully")
except Exception as e:
    print(f"[API] WARNING: Could not load all resources: {e}")
    import traceback
    traceback.print_exc()


def handler(event, context=None):
    """Entry point for Vercel serverless function."""
    try:
        # Handle both direct request object and Vercel event format
        if isinstance(event, dict):
            # Vercel event format
            request = VercelRequest(event)
        else:
            # Direct request object
            request = event
        
        # Call backend handler
        response_body, status_code, response_headers = handle_request(request)
        
        # Ensure response is JSON string
        if not isinstance(response_body, str):
            response_body = json.dumps(response_body)
        
        # Merge headers
        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept, Origin",
            **response_headers
        }
        
        return {
            "statusCode": status_code,
            "headers": headers,
            "body": response_body
        }
        
    except Exception as e:
        print(f"[API] Handler error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": f"Server error: {str(e)}"})
        }
