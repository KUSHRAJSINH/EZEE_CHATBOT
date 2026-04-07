from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()


def llm_model(model: str = "llama-3.1-8b-instant") -> ChatGroq:
    
    llm = ChatGroq(
        model=model,
        temperature=0.5,
        timeout=20,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    return llm