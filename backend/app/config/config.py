from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    APP_NAME = "WebForge AI"
    APP_VERSION = "1.0.0"

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

settings = Settings()