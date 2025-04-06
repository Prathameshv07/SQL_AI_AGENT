from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from dotenv import load_dotenv
from pydantic import BaseModel
import json
import asyncio
from app.services.ai_service import convert_nl_to_sql_with_feedback
from app.services.sql_service import execute_sql_query
from fastapi.responses import StreamingResponse


# Load environment variables
load_dotenv()


class QueryRequest(BaseModel):
    query: str


app = FastAPI(title="SQL AI AGENT")


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Templates
templates = Jinja2Templates(directory="templates")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/query")
async def process_query(request: QueryRequest):
    try:
        # Use the robust method with feedback for better results
        result = await convert_nl_to_sql_with_feedback(request.query)
        
        if result["status"] != "success":
            raise Exception(f"Failed to generate SQL: {result['error']}")
        
        # Execute SQL query and get results
        results = execute_sql_query(result["sql"])
        
        return {
            "original_query": request.query,
            "sql_query": result["sql"],
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post("/api/feedback")
async def process_feedback(feedback_data: dict):
    # Log the error data for monitoring and improvement
    print("Received error feedback:", feedback_data)
    
    # You could store this in a database for later analysis
    # or send it to a logging service
    
    return {"status": "received"}


@app.post("/api/convert-query")
async def convert_query(request: QueryRequest):
    async def generate():
        # Start the conversion process
        result = {"status": "processing"}
        yield json.dumps(result).encode() + b"\n"
        
        try:
            # Initial attempt with unified function
            conversion_result = await convert_nl_to_sql_with_feedback(request.query)
            
            # Stream status updates to frontend
            while conversion_result["status"] == "retrying":
                # Send retry status with all necessary info
                yield json.dumps({
                    "status": "retrying",
                    "retry_count": conversion_result["retry_count"],
                    "error": conversion_result["error"],
                    "query": request.query,
                    "schema": conversion_result["schema"]
                }).encode() + b"\n"
                
                # Wait briefly
                await asyncio.sleep(0.5)
                
                # Continue processing with error feedback
                conversion_result = await convert_nl_to_sql_with_feedback(
                    request.query, 
                    error_msg=conversion_result["error"]
                )
            
            # Final result - either success or failed
            yield json.dumps(conversion_result).encode() + b"\n"
            
        except Exception as e:
            # Handle unexpected errors with full context
            error_result = {
                "status": "failed",
                "error": str(e),
                "sql": None,
                "retry_count": 0,
                "query": request.query,
                "schema": conversion_result.get("schema", "Schema not available")
            }
            yield json.dumps(error_result).encode() + b"\n"

    return StreamingResponse(
        generate(),
        media_type="application/json"
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)