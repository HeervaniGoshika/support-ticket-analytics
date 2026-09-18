from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration.

    Values can be supplied through environment variables
    or a .env file.
    """

    app_name: str = "DOTMappers AI Support Intelligence"
    app_version: str = "1.0.0"

    # Database
    database_url: str = "sqlite:///./data/support_tickets.db"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Anomaly detection
    unresolved_age_hours: float = 24.0
    isolation_contamination: float = 0.05

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()