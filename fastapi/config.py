from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL
    DATABASE_URL: str = ""

    # Vertex AI (primario — inferencia + embeddings)
    VERTEX_SA_JSON_PATH: str = "secrets/my-project-1-498507-f9afb01caaa5.json"
    VERTEX_PROJECT_ID: str = "my-project-1-498507"
    VERTEX_LOCATION: str = "us-central1"
    VERTEX_INFERENCE_MODEL: str = "gemini-2.5-flash"
    VERTEX_EMBED_MODEL: str = "gemini-embedding-001"
    VERTEX_EMBED_DIM: int = 1536

    # Fallback chain (provisional — migrar a nodos system en BD)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    NVIDIA_NIM_API_KEY: str = ""
    NVIDIA_MODEL: str = "meta/llama-3.3-70b-instruct"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"  # 7b garantizado en RAM disponible

    # FastAPI
    FASTAPI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

