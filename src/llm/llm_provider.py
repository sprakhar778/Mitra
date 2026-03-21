from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

def get_llm_provider(provider:str="openai",model_name: str = "gpt-4o") -> ChatGroq | ChatOpenAI:
    """Factory function to get the appropriate LLM provider based on configuration."""
    if provider == "groq":
        return ChatGroq(model=model_name)
    elif provider == "openai":
        return ChatOpenAI(model=model_name)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")