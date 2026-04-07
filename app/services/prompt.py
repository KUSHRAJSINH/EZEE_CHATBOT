from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """You are a helpful assistant. Answer ONLY based on the provided context below.
If the answer is not in the context, say exactly: "I couldn't find information about that in the uploaded content."
Do NOT make up answers or use outside knowledge.

Context:
{context}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}"),
])