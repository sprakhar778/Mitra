from pydantic_settings import BaseSettings, SettingsConfigDict


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


        





settings = Settings()
   