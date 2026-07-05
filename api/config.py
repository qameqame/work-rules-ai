from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_base_url: str
    llm_model: str
    chroma_host: str
    chroma_internal_port: int
    embed_model: str
    chunk_size: int = 200
    chunk_overlap: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
