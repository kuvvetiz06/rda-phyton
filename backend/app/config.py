from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    ollama_base_url: str = "http://localhost:11434"
    llm_model_name: str = "llama3:8b"

    class Config:
        env_prefix = ""
        case_sensitive = False


settings = Settings()
