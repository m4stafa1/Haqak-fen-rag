from fastapi import APIRouter
from app.schemas.query import QueryRequest, QueryResponse
from app.services.retrieval import retrieve
from app.services.generation import generate_answer

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    chunks = retrieve(request.question)
    answer = generate_answer(request.question, chunks)
    sources = list(dict.fromkeys(c["source"] for c in chunks))  # إزالة تكرار المصادر
    return QueryResponse(answer=answer, sources=sources)