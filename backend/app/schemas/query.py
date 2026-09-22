from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="سؤال المستخدم بخصوص حقوق المستهلك")

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]