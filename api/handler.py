"""
Vercel-compatible API handler for MedSafeAI Backend
Wraps the business logic from index.py
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# Import the backend logic
from api.index import (
    handle_request as backend_handle_request,
    load_resources
)

# Load resources once at module import
print("[VERCEL] Initializing MedSafeAI backend...")
try:
    load_resources()
    print("[VERCEL] Backend initialized successfully")
except Exception as e:
    print(f"[VERCEL] ERROR during initialization: {e}")
    import traceback
    traceback.print_exc()


class MockRequest:
    """Mock HTTP request object for Vercel event"""
    def __init__(self, event):
        self.path = event.get("path", "/")
        self.method = event.get("method", "GET").upper()
        self.headers = event.get("headers", {})
        self.body = event.get("body", "")
        self.query_string = event.get("query_string", "")
        
        # Parse path parameters if needed
        if "path" in event:
            self.path = event["path"]


def handler(event, context):
    """
    Vercel serverless function handler.
    Receives HTTP event from Vercel and returns response.
    """
    try:
        print(f"[VERCEL] Received request: {event.get('method', 'GET')} {event.get('path', '/')}")
        
        # Create mock request
        request = MockRequest(event)
        
        # Call backend handler
        response_body, status_code, headers = backend_handle_request(request)
        
        # Ensure response_body is JSON string
        if isinstance(response_body, dict):
            response_body = json.dumps(response_body)
        elif not isinstance(response_body, str):
            response_body = json.dumps({"error": "Invalid response type"})
        
        # Return Vercel format
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Accept, Origin",
                **headers
            },
            "body": response_body
        }
        
    except Exception as e:
        print(f"[VERCEL] ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }
