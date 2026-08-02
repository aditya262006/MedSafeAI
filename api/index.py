"""
MedSafeAI Backend - Vercel Serverless Function
Pure Python implementation - NO external ML dependencies
"""

import json
from typing import Tuple, Dict, Any

# ═══════════════════════════════════════════════════════════════════════════════
# DRUG KNOWLEDGE BASE - Pure Python, No Dependencies
# ═══════════════════════════════════════════════════════════════════════════════

DRUG_DATABASE = {
    "aspirin": {
        "common_uses": "Pain relief, fever, inflammation, heart attack prevention",
        "risk_level": "Low",
        "severity_score": 3.5,
        "serious_event_rate": 0.02,
        "interactions": ["warfarin", "ibuprofen", "naproxen", "methotrexate"],
        "side_effects": ["stomach upset", "bleeding risk", "allergic reactions"]
    },
    "ibuprofen": {
        "common_uses": "Pain relief, fever, inflammation",
        "risk_level": "Low",
        "severity_score": 4.0,
        "serious_event_rate": 0.03,
        "interactions": ["aspirin", "warfarin", "methotrexate", "lithium"],
        "side_effects": ["stomach upset", "kidney problems", "dizziness"]
    },
    "warfarin": {
        "common_uses": "Blood thinner, prevent blood clots, stroke prevention",
        "risk_level": "High",
        "severity_score": 8.0,
        "serious_event_rate": 0.15,
        "interactions": ["aspirin", "ibuprofen", "naproxen", "acetaminophen", "cranberry"],
        "side_effects": ["severe bleeding", "bruising", "hair loss", "skin necrosis"]
    },
    "metformin": {
        "common_uses": "Diabetes management, blood sugar control",
        "risk_level": "Low",
        "severity_score": 3.0,
        "serious_event_rate": 0.01,
        "interactions": ["alcohol", "contrast dye", "cimetidine"],
        "side_effects": ["nausea", "diarrhea", "metallic taste", "vitamin b12 deficiency"]
    },
    "lisinopril": {
        "common_uses": "High blood pressure, heart failure, heart attack prevention",
        "risk_level": "Medium",
        "severity_score": 5.5,
        "serious_event_rate": 0.05,
        "interactions": ["potassium supplements", "nsaids", "diuretics", "lithium"],
        "side_effects": ["dizziness", "persistent dry cough", "fatigue", "hyperkalemia"]
    },
    "metoprolol": {
        "common_uses": "High blood pressure, heart disease, migraine prevention",
        "risk_level": "Medium",
        "severity_score": 5.0,
        "serious_event_rate": 0.04,
        "interactions": ["calcium channel blockers", "digoxin", "verapamil"],
        "side_effects": ["fatigue", "dizziness", "slow heart rate", "depression"]
    },
    "atorvastatin": {
        "common_uses": "Cholesterol management, cardiovascular protection",
        "risk_level": "Low",
        "severity_score": 4.0,
        "serious_event_rate": 0.02,
        "interactions": ["clarithromycin", "erythromycin", "gemfibrozil", "niacin"],
        "side_effects": ["muscle pain", "weakness", "liver problems", "headache"]
    },
    "acetaminophen": {
        "common_uses": "Pain relief, fever reduction",
        "risk_level": "Low",
        "severity_score": 3.5,
        "serious_event_rate": 0.02,
        "interactions": ["warfarin", "alcohol", "isoniazid"],
        "side_effects": ["liver damage with overdose", "allergic reaction", "rash"]
    },
    "amoxicillin": {
        "common_uses": "Bacterial infection treatment, antibiotic",
        "risk_level": "Low",
        "severity_score": 2.5,
        "serious_event_rate": 0.01,
        "interactions": ["birth control pills", "warfarin", "methotrexate"],
        "side_effects": ["allergic reaction", "diarrhea", "rash", "nausea"]
    },
    "omeprazole": {
        "common_uses": "Acid reflux, ulcer treatment, GERD management",
        "risk_level": "Low",
        "severity_score": 3.0,
        "serious_event_rate": 0.01,
        "interactions": ["clopidogrel", "digoxin", "levothyroxine"],
        "side_effects": ["headache", "nausea", "diarrhea", "vitamin b12 deficiency"]
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS - Pure Python
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_risk_level(drug_info: Dict) -> Tuple[str, float]:
    """Calculate risk level based on drug properties - Pure Python logic."""
    severity = drug_info.get("severity_score", 5.0)
    serious_rate = drug_info.get("serious_event_rate", 0.05)
    
    # Simple rule-based scoring
    score = 0
    
    if severity >= 7.0:
        score += 3
    elif severity >= 5.0:
        score += 2
    else:
        score += 1
    
    if serious_rate >= 0.10:
        score += 3
    elif serious_rate >= 0.05:
        score += 2
    else:
        score += 1
    
    if score >= 5:
        return "High", 0.85
    elif score >= 3:
        return "Medium", 0.55
    else:
        return "Low", 0.25


def find_interactions_between(drug_list: list) -> list:
    """Find drug-drug interactions."""
    interactions = []
    for i in range(len(drug_list)):
        for j in range(i + 1, len(drug_list)):
            drug_a = drug_list[i]
            drug_b = drug_list[j]
            
            if drug_a in DRUG_DATABASE:
                interactions_for_a = DRUG_DATABASE[drug_a].get("interactions", [])
                if drug_b in interactions_for_a:
                    interactions.append({
                        "drug_a": drug_a,
                        "drug_b": drug_b,
                        "severity": "High",
                        "description": f"Potential interaction between {drug_a.title()} and {drug_b.title()}"
                    })
    
    return interactions


# ═══════════════════════════════════════════════════════════════════════════════
# API REQUEST HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

def handle_request(request) -> Tuple[str, int, Dict]:
    """Handle HTTP request and return (body, status_code, headers)."""
    
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Accept, Origin",
    }
    
    path = request.path
    method = request.method
    
    print(f"[API] {method} {path}")
    
    # CORS preflight
    if method == "OPTIONS":
        return (json.dumps({"ok": True}), 200, headers)
    
    try:
        # Health check endpoint
        if path in ["/", "/health", "/api/health"]:
            return (
                json.dumps({
                    "status": "healthy",
                    "message": "MedSafeAI backend is running",
                    "drugs_available": len(DRUG_DATABASE)
                }),
                200,
                headers
            )
        
        # Search endpoint
        if path in ["/search", "/api/search"]:
            q = request.args.get("q", "").strip().lower()
            
            if not q:
                return (json.dumps({"error": "Query parameter 'q' is required"}), 400, headers)
            
            # Search for matching drugs
            matches = [
                drug for drug in DRUG_DATABASE.keys()
                if q in drug.lower()
            ]
            
            # Sort: exact matches first, then by length
            matches.sort(key=lambda x: (x != q, len(x)))
            
            return (
                json.dumps({
                    "suggestions": matches[:10],
                    "query": q,
                    "count": len(matches)
                }),
                200,
                headers
            )
        
        # Predict endpoint
        if path in ["/predict", "/api/predict"]:
            if method != "POST":
                return (json.dumps({"error": "POST method required"}), 405, headers)
            
            data = request.json or {}
            drugs = data.get("drugs", [])
            
            if not isinstance(drugs, list) or not drugs:
                return (
                    json.dumps({"error": "Request must include 'drugs' array"}),
                    400,
                    headers
                )
            
            if len(drugs) > 10:
                return (
                    json.dumps({"error": "Maximum 10 drugs per request"}),
                    400,
                    headers
                )
            
            # Normalize drug names to lowercase
            drugs_normalized = [d.lower().strip() for d in drugs]
            
            # Analyze each drug
            results = []
            max_risk_score = 0
            
            for drug_name in drugs_normalized:
                if drug_name in DRUG_DATABASE:
                    drug_info = DRUG_DATABASE[drug_name]
                    risk_level, risk_score = calculate_risk_level(drug_info)
                    max_risk_score = max(max_risk_score, risk_score)
                    
                    results.append({
                        "drug": drug_name,
                        "found": True,
                        "risk_level": risk_level,
                        "risk_score": round(risk_score, 2),
                        "severity_score": drug_info.get("severity_score", 0),
                        "serious_event_rate": drug_info.get("serious_event_rate", 0),
                        "side_effects": drug_info.get("side_effects", []),
                        "common_uses": drug_info.get("common_uses", "")
                    })
                else:
                    results.append({
                        "drug": drug_name,
                        "found": False,
                        "risk_level": "Unknown",
                        "risk_score": 0.5,
                        "error": "Drug not in database"
                    })
            
            # Find interactions
            interactions = find_interactions_between(drugs_normalized)
            
            # Determine overall risk
            if interactions:
                overall_risk = "High"
            elif any(r["risk_level"] == "High" for r in results if r.get("found")):
                overall_risk = "High"
            elif any(r["risk_level"] == "Medium" for r in results if r.get("found")):
                overall_risk = "Medium"
            else:
                overall_risk = "Low"
            
            return (
                json.dumps({
                    "results": results,
                    "interactions": interactions,
                    "overall_risk": overall_risk,
                    "interaction_count": len(interactions),
                    "recommendation": "Always consult with a healthcare provider before combining medications."
                }),
                200,
                headers
            )
        
        # Drug info endpoint
        if path.startswith("/api/drug/") or path.startswith("/drug/"):
            drug_name = path.split("/")[-1].lower()
            
            if drug_name not in DRUG_DATABASE:
                return (
                    json.dumps({"error": f"Drug '{drug_name}' not found"}),
                    404,
                    headers
                )
            
            drug_info = DRUG_DATABASE[drug_name]
            return (
                json.dumps({
                    "drug": drug_name,
                    "info": drug_info
                }),
                200,
                headers
            )
        
        # 404 - Not found
        return (
            json.dumps({"error": "Endpoint not found. Available: /health, /search, /predict, /drug/{name}"}),
            404,
            headers
        )
        
    except Exception as e:
        print(f"[API] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return (
            json.dumps({"error": f"Server error: {str(e)}"}),
            500,
            headers
        )


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


print("[API] MedSafeAI backend initialized")


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
