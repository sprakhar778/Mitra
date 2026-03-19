from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",extra="ignore")

    OPENAI_API_KEY: str
    GROQ_API_KEY: str
    GROQ_IMAGE_MODEL_NAME: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    ELEVENLABS_API_KEY: str
    ELEVENLABS_VOICE_ID: str
    





settings = Settings()
   