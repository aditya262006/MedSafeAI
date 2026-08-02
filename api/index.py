"""MedSafeAI Backend - Minimal Pure Python for Vercel"""
import json
from urllib.parse import parse_qs

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

def handler(request, response=None):
    """Main handler for Vercel serverless function"""
    
    # Parse request
    method = request.method
    path = request.path
    
    # CORS headers
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    
    # Handle OPTIONS
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": ""}
    
    try:
        # Health endpoint
        if path == "/" or path == "/api/health" or path == "/health":
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"status": "healthy", "drugs": len(DRUGS)})
            }
        
        # Search endpoint
        if path == "/api/search" or path == "/search":
            q = request.args.get("q", "").lower().strip()
            results = [d for d in DRUGS if q in d]
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"suggestions": results[:10], "query": q})
            }
        
        # Predict endpoint
        if path == "/api/predict" or path == "/predict":
            if method != "POST":
                return {"statusCode": 405, "headers": headers, "body": json.dumps({"error": "POST required"})}
            
            data = request.json or {}
            drugs = data.get("drugs", [])
            
            if not drugs:
                return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "No drugs provided"})}
            
            results = []
            interactions = []
            
            for drug in drugs:
                drug = drug.lower()
                if drug in DRUGS:
                    info = DRUGS[drug]
                    results.append({
                        "drug": drug,
                        "risk_level": info["risk"],
                        "uses": info["uses"]
                    })
            
            # Find interactions
            for i in range(len(drugs)):
                for j in range(i+1, len(drugs)):
                    d1 = drugs[i].lower()
                    d2 = drugs[j].lower()
                    if d1 in DRUGS and d2 in DRUGS[d1].get("interactions", []):
                        interactions.append({"drug_a": d1, "drug_b": d2})
            
            overall_risk = "High" if interactions else ("Medium" if any(r["risk_level"] == "Medium" for r in results) else "Low")
            
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "results": results,
                    "interactions": interactions,
                    "overall_risk": overall_risk
                })
            }
        
        return {"statusCode": 404, "headers": headers, "body": json.dumps({"error": "Not found"})}
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }
