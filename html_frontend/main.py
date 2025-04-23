import os
import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any

load_dotenv()

app = FastAPI()

# Mount static files (like index.html, css, js if any)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates directory
templates = Jinja2Templates(directory="static")

# Superlinked API URL (from environment variable or default)
SUPERLINKED_API_URL = os.getenv("SUPERLINKED_API_URL", "http://localhost:8080")

# Helper function to format response from Superlinked
def format_superlinked_response(response_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Transforms the Superlinked API response into a flat list of hotel dicts."""
    results = []
    # Use "entries" key based on observed curl response
    if response_json and isinstance(response_json, dict) and "entries" in response_json:
        for row in response_json["entries"]:
            obj = row.get("fields", {}) 
            score = row.get("metadata", {}).get("score", 0.0) 
            
            # Combine obj fields, score, id, and image_src
            hotel_data = {
                "id": row.get("id"), 
                "image_src": row.get("image_src"), # Explicitly add image_src from top level
                **obj, 
                "score": score
            }
            results.append(hotel_data)
    return results

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/search")
async def search_hotels(
    query: Optional[str] = Query(None),

    limit: int = Query(20),
    offset: int = Query(0) 
):
    """Proxy search requests to the Superlinked backend API.""" # Simplified docstring
    
    # Construct the main payload dictionary
    payload = {
        "natural_query": query,
        "limit": limit,
    }


    async with httpx.AsyncClient() as client:
        try:
            # Corrected path based on Superlinked API docs (/docs)
            api_endpoint = f"{SUPERLINKED_API_URL}/api/v1/search/hotel" 
            print(f"Querying Superlinked API: {api_endpoint} with payload: {payload}") # Debug print

            response = await client.post(api_endpoint, json=payload)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Format the results part of the response
            formatted_results = format_superlinked_response(response_data)
            
            # Extract debug parameters (knn_params) if available
            debug_params = response_data.get("metadata", {}).get("debug_data", {}).get("knn_params", {})
            
            # Return both results and debug params to the frontend
            return {"results": formatted_results, "debug_params": debug_params}
            
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            raise HTTPException(status_code=503, detail=f"Superlinked API request failed: {exc}")
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            # Forward the error details if possible
            error_detail = f"Superlinked API returned status {exc.response.status_code}"
            try:
                error_detail += f": {exc.response.json()}"
            except Exception:
                pass # Ignore if response body isn't valid JSON
            raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 