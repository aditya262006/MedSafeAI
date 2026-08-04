"""
MedSafeAI Backend - Render Deployment
Pure Python Flask App
"""
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Drug database
DRUGS = {
    "aspirin": {"risk": "Low", "interactions": ["warfarin", "ibuprofen"], "uses": "Pain relief, fever"},
    "warfarin": {"risk": "High", "interactions": ["aspirin", "ibuprofen"], "uses": "Blood thinner"},
    "ibuprofen": {"risk": "Low", "interactions": ["aspirin", "warfarin"], "uses": "Pain relief"},
    "metformin": {"risk": "Low", "interactions": [], "uses": "Diabetes management"},
    "lisinopril": {"risk": "Medium", "interactions": [], "uses": "Blood pressure"},
    "metoprolol": {"risk": "Medium", "interactions": [], "uses": "Heart disease"},
    "atorvastatin": {"risk": "Low", "interactions": [], "uses": "Cholesterol"},
    "acetaminophen": {"risk": "Low", "interactions": [], "uses": "Pain relief"},
    "amoxicillin": {"risk": "Low", "interactions": [], "uses": "Antibiotic"},
    "omeprazole": {"risk": "Low", "interactions": [], "uses": "Acid reflux"},
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "MedSafeAI Backend",
        "drugs_available": len(DRUGS)
    })

@app.route('/api/health', methods=['GET'])
def api_health():
    return health()

@app.route('/api/search', methods=['GET'])
def search():
    q = request.args.get('q', '').lower().strip()
    
    if not q:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    results = [drug for drug in DRUGS.keys() if q in drug]
    results.sort(key=lambda x: (x != q, len(x)))
    
    return jsonify({
        "suggestions": results[:10],
        "query": q,
        "count": len(results)
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json() or {}
    drugs = data.get('drugs', [])
    
    if not drugs:
        return jsonify({"error": "Request must include 'drugs' array"}), 400
    
    if len(drugs) > 10:
        return jsonify({"error": "Maximum 10 drugs per request"}), 400
    
    # Normalize and analyze drugs
    results = []
    interactions = []
    max_risk = "Low"
    
    drugs_lower = [d.lower() for d in drugs]
    
    for drug in drugs_lower:
        if drug in DRUGS:
            info = DRUGS[drug]
            results.append({
                "drug": drug,
                "found": True,
                "risk_level": info["risk"],
                "uses": info["uses"]
            })
            
            # Update max risk
            if info["risk"] == "High":
                max_risk = "High"
            elif info["risk"] == "Medium" and max_risk != "High":
                max_risk = "Medium"
        else:
            results.append({
                "drug": drug,
                "found": False,
                "risk_level": "Unknown",
                "error": "Drug not in database"
            })
    
    # Find interactions
    for i in range(len(drugs_lower)):
        for j in range(i + 1, len(drugs_lower)):
            d1 = drugs_lower[i]
            d2 = drugs_lower[j]
            if d1 in DRUGS and d2 in DRUGS[d1].get("interactions", []):
                interactions.append({
                    "drug_a": d1,
                    "drug_b": d2,
                    "severity": "High"
                })
                max_risk = "High"
    
    overall_risk = max_risk
    
    return jsonify({
        "results": results,
        "interactions": interactions,
        "overall_risk": overall_risk,
        "recommendation": "Always consult with a healthcare provider before combining medications."
    })

@app.route('/api/drug/<name>', methods=['GET'])
def drug_info(name):
    name = name.lower()
    
    if name not in DRUGS:
        return jsonify({"error": f"Drug '{name}' not found"}), 404
    
    return jsonify({
        "drug": name,
        "info": DRUGS[name]
    })

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "MedSafeAI Backend",
        "status": "running",
        "endpoints": [
            "GET /health",
            "GET /api/health",
            "GET /api/search?q=drug_name",
            "POST /api/predict",
            "GET /api/drug/{name}"
        ]
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
