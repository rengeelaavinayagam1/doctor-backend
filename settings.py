from pydantic import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    MONGO_URI: str = "mongodb+srv://23uea036_db_user:Sri@2k05_@cluster0.jcrbluz.mongodb.net/?appName=Cluster0"
    JWT_SECRET: str = "changeme"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()