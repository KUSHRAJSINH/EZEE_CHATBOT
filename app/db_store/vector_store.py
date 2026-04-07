from langchain_community.vectorstores import Chroma
from services.embedding import model  # shared embedding function


CHROMA_BASE_DIR = "chroma_db"



def get_vector_store(bot_id: str) -> Chroma:
    
    return Chroma(
        collection_name=f"bot_{bot_id}",
        persist_directory=f"{CHROMA_BASE_DIR}/{bot_id}",
        embedding_function=model,
    )
