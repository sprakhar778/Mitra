from pydantic_settings import BaseSettings, SettingsConfigDict
import os



# ✅ Resolve path safely (independent of cwd)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src/core
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../"))

DB_PATH = os.path.join(PROJECT_ROOT, "src/data/memory.db")

# ✅ Ensure directory exists (important)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",extra="ignore")

    OPENAI_API_KEY: str| None = None
    GROQ_API_KEY: str| None = None


    GROQ_IMAGE_MODEL_NAME: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    
   

    GOOGLE_API_KEY: str| None = None
    IMAGE_GENERATION_MODEL_NAME: str| None = "gemini-2.5-flash-image"

    DEEPGRAM_API_KEY: str| None = None
    DEEPGRAM_SPEECH_MODEL_NAME: str| None = "aura-2-aries-en"

    SPEECH_TO_TEXT_MODEL_NAME: str| None = "whisper-large-v3-turbo"


    QDRANT_API_KEY: str | None = None
    QDRANT_URL: str| None = "https://cd59c1e1-dfde-4db3-a4db-c4ef7d3275d8.eu-west-2-0.aws.cloud.qdrant.io"
    QDRANT_PORT: str = "6333"
    QDRANT_HOST: str | None = None

    MEMORY_TOP_K: int = 3
    ROUTER_MESSAGES_TO_ANALYZE: int = 3
    TOTAL_MESSAGES_SUMMARY_TRIGGER: int = 15
    TOTAL_MESSAGES_AFTER_SUMMARY: int = 5

    SHORT_TERM_MEMORY_DB_PATH: str = DB_PATH

      



settings = Settings()
   