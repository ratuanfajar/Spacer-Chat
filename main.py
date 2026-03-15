from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from rag.chain import RAGChain
from app.config import settings

app = FastAPI(
    title="Spacer Chat - RAG API",
    description="RAG Backend API",
    version="1.0.0"
)

# Model
class ChatRequest(BaseModel):
    """Chat request model."""
    question: str
    
class ChatResponse(BaseModel):
    """Chat response model."""
    content: str
    suggested_questions: List[str] = []

# Routes
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Selamat datang di Spacer Chat API!",
        "service": "RAG Chatbot Backend",
        "ui": "Streamlit UI",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "ask": "/ask"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "spacer-chat"}

@app.post("/ask", response_model=ChatResponse)
def ask(request: ChatRequest):
    """
    Main chat endpoint.
    
    Usage:
    POST /ask
    {
        "question": "Apa itu neural network?"
    }
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        rag_chain = RAGChain()
        
        result = rag_chain.run(request.question)
        
        return ChatResponse(
            content=result.get('content', 'Tidak ada jawaban'),
            suggested_questions=result.get('suggested_questions', [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Spacer Chat FastAPI Backend")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )