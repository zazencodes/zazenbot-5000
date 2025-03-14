import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from query_rag_with_metadata import process_question

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ZazenBot 5000 API",
    description="API for querying RAG with metadata",
    version="1.0.0",
)

class QuestionRequest(BaseModel):
    question: str

@app.post("/query", response_class=PlainTextResponse)
async def query(request: QuestionRequest):
    """
    Process a question through the RAG system and enhance with metadata and timestamp
    """
    try:
        logger.info(f"Received question: {request.question}")
        response = process_question(request.question)
        return response
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
