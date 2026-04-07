from db_store.vector_store import get_vector_store
from typing import List


def retrieve_chunks(query: str, bot_id: str, k: int = 5) -> List[str]:
    #breakpoint()
    vector_store = get_vector_store(bot_id)
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(query)
    return [doc.page_content for doc in docs]