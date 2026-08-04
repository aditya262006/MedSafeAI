import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Drug database
DRUGS = {
    "aspirin": {"risk": "Low", "interactions": ["warfarin", "ibuprofen"], "uses": "Pain relief"},
    "warfarin": {"risk": "High", "interactions": ["aspirin", "ibuprofen"], "uses": "Blood thinner"},
    "ibuprofen": {"risk": "Low", "interactions": ["aspirin", "warfarin"], "uses": "Pain relief"},
    "metformin": {"risk": "Low", "interactions": [], "uses": "Diabetes"},
    "lisinopril": {"risk": "Medium", "interactions": [], "uses": "Blood pressure"},
    "metoprolol": {"risk": "Medium", "interactions": [], "uses": "Heart disease"},
    "atorvastatin": {"risk": "Low", "interactions": [], "uses": "Cholesterol"},
    "acetaminophen": {"risk": "Low", "interactions": [], "uses": "Pain relief"},
    "amoxicillin": {"risk": "Low", "interactions": [], "uses": "Antibiotic"},
    "omeprazole": {"risk": "Low", "interactions": [], "uses": "Acid reflux"},
}

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "MedSafeAI Backend API", "status": "running", "endpoints": ["/health", "/api/search", "/api/predict"]})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "drugs": len(DRUGS)})

@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"status": "healthy", "drugs": len(DRUGS)})

@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("q", "").lower().strip()
    if not q:
        return jsonify({"error": "Query required"}), 400
    results = [d for d in DRUGS if q in d]
    return jsonify({"suggestions": results[:10], "query": q})

@app.route("/api/search", methods=["GET"])
def api_search():
    q = request.args.get("q", "").lower().strip()
    if not q:
        return jsonify({"error": "Query required"}), 400
    results = [d for d in DRUGS if q in d]
    return jsonify({"suggestions": results[:10], "query": q})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json() or {}
    drugs = data.get("drugs", [])
    
    if not drugs:
        return jsonify({"error": "No drugs provided"}), 400
    
    results = []
    for drug in drugs:
        drug = drug.lower()
        if drug in DRUGS:
            info = DRUGS[drug]
            results.append({
                "drug": drug,
                "risk_level": info["risk"],
                "uses": info["uses"]
            })
    
    interactions = []
    for i in range(len(drugs)):
        for j in range(i+1, len(drugs)):
            d1 = drugs[i].lower()
            d2 = drugs[j].lower()
            if d1 in DRUGS and d2 in DRUGS[d1].get("interactions", []):
                interactions.append({"drug_a": d1, "drug_b": d2})
    
    overall_risk = "High" if interactions else ("Medium" if any(r["risk_level"] == "Medium" for r in results) else "Low")
    
    return jsonify({
        "results": results,
        "interactions": interactions,
        "overall_risk": overall_risk
    })

@app.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json() or {}
    drugs = data.get("drugs", [])
    
    if not drugs:
        return jsonify({"error": "No drugs provided"}), 400
    
    results = []
    for drug in drugs:
        drug = drug.lower()
        if drug in DRUGS:
            info = DRUGS[drug]
            results.append({
                "drug": drug,
                "risk_level": info["risk"],
                "uses": info["uses"]
            })
    
    interactions = []
    for i in range(len(drugs)):
        for j in range(i+1, len(drugs)):
            d1 = drugs[i].lower()
            d2 = drugs[j].lower()
            if d1 in DRUGS and d2 in DRUGS[d1].get("interactions", []):
                interactions.append({"drug_a": d1, "drug_b": d2})
    
    overall_risk = "High" if interactions else ("Medium" if any(r["risk_level"] == "Medium" for r in results) else "Low")
    
    return jsonify({
        "results": results,
        "interactions": interactions,
        "overall_risk": overall_risk
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
