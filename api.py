"""
FastAPI REST layer for Canonical Data Schema Alignment System.

Exposes the analyze_csv_schema() function via HTTP endpoints.
"""

import tempfile
import os
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.alignment_service import analyze_csv_schema

# Initialize FastAPI app
app = FastAPI(
    title="Canonical Alignment API",
    description="REST API for schema alignment and mapping",
    version="1.0.0"
)

# Add CORS middleware (allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "canonical-alignment-api"}


@app.post("/api/align")
async def align_csv(file: UploadFile = File(...)):
    """
    Analyze CSV schema and generate canonical mappings.
    
    Args:
        file: CSV file upload (multipart/form-data, field: "file")
    
    Returns:
        {"accepted": [...], "review_item_ids": [...]}
    
    Raises:
        HTTPException: 500 if analysis fails
    """
    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".csv",
            delete=False
        ) as tmp:
            temp_file = tmp.name
            # Write uploaded file to temp location
            contents = await file.read()
            tmp.write(contents)
        
        # Call the alignment service
        result = analyze_csv_schema(temp_file)
        
        # Return result as JSON
        return result
        
    except Exception as e:
        # Return 500 error with message
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)}
        )
    
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass  # Ignore cleanup errors


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
