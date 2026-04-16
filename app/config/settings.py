from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    MONGO_URI: str = "mongodb://localhost:27017/smart_doctor_db"
    JWT_SECRET: str = "changeme"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()