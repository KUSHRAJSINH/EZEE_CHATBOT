from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()


model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def embeddings(chunks):
    return model.embed_documents(chunks)