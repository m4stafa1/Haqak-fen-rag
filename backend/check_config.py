from app.core.config import settings


print("App:", settings.app_name)
print("Vector Store:", settings.vector_store_path)
print("Collection:", settings.collection_name)
print("Embedding:", settings.embedding_model)
print("Ollama:", settings.ollama_model)