from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    vector_store_path: str
    collection_name: str
    embedding_model: str
    ollama_model: str
    cors_origins: str = "http://localhost:8501"

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

settings = Settings()