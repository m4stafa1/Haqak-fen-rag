from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.query import router as query_router
from app.services.retrieval import load_vector_store
from app.utils.logging_config import setup_logging
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    load_vector_store()   # الموديل والـ vector store يتحملوا مرة واحدة هنا بس
    yield

app = FastAPI(title="Haqak Fen API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router)