from langchain_openai import ChatOpenAI
from app.config import settings

def get_llm():
    return ChatOpenAI(
        model=settings.MODEL_NAME,        
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_BASE_URL,
        temperature=0.3,                   
        streaming=True
    )