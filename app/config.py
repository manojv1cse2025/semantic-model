from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    database_url: str = (
        "postgresql+psycopg://"
        "semantic:semantic_password@"
        "localhost:5432/semanticdb"
    )

    google_api_key: str

    embedding_model: str = "models/text-embedding-004"

    embedding_dimensions: int = 768

    model_name: str = "gemini-3.6-flash"

    class Config:
        env_file = ".env"


settings = Settings()
