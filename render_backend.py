"""
MedSafeAI Backend - Render Deployment
Serves both backend API and frontend from single deployment
"""
import json
import os
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Frontend static files - try multiple possible paths
POSSIBLE_FRONTEND_PATHS = [
    Path(__file__).parent.parent / 'frontend' / 'dist',
    Path(__file__).parent / 'frontend' / 'dist',
    Path(__file__).parent / 'dist',
    Path('/opt/render/project/src/frontend/dist'),
]

FRONTEND_DIST = None
for path in POSSIBLE_FRONTEND_PATHS:
    if path.exists() and (path / 'index.html').exists():
        FRONTEND_DIST = path
        print(f"✅ Found frontend at: {FRONTEND_DIST}")
        break

if FRONTEND_DIST is None:
    print("⚠️ Frontend dist folder not found, running in API-only mode")

app = Flask(__name__, static_folder=str(FRONTEND_DIST) if FRONTEND_DIST else None, static_url_path='')
CORS(app, origins="*")

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

@app.route('/search', methods=['GET'])
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

@app.route('/predict', methods=['POST'])
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

@app.route('/drug/<name>', methods=['GET'])
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
    """Serve frontend index.html if available, otherwise API info"""
    if FRONTEND_DIST:
        try:
            index_file = FRONTEND_DIST / 'index.html'
            if index_file.exists():
                return send_from_directory(str(FRONTEND_DIST), 'index.html')
        except Exception as e:
            print(f"Error serving index.html: {e}")
    
    return jsonify({
        "service": "MedSafeAI Backend",
        "status": "running",
        "frontend_available": FRONTEND_DIST is not None,
        "frontend_path": str(FRONTEND_DIST) if FRONTEND_DIST else "Not found",
        "endpoints": [
            "GET /health",
            "GET /search?q=drug_name",
            "POST /predict",
            "GET /drug/{name}"
        ]
    })

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Serve frontend static files if available"""
    if FRONTEND_DIST:
        try:
            file_path = FRONTEND_DIST / path
            if file_path.exists():
                return send_from_directory(str(FRONTEND_DIST), path)
        except Exception as e:
            print(f"Error serving static file {path}: {e}")
    
    return jsonify({"error": "Not found", "path": path}), 404

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
