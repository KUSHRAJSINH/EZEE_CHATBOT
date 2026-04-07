from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

def chunk_text(text:str)-> List[str]:
    

    if not text or not text.strip():
        return []
    
    splitter= RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=[
            "\n\n", #paragraph
            "\n",   #line
            ".",    #sentence
            " ",    #word
            ""      #fallback 
        ]
    )

    chunks=splitter.split_text(text)

    #quality chunk

    cleaned_chunks= [chunk.strip() for chunk in chunks if chunk.strip()]

    return cleaned_chunks


def chunk_text_with_metadata(text: str):
    chunks = chunk_text(text)

    return [
        {
            "chunk": chunk,
            "length": len(chunk)
        }
        for chunk in chunks
    ]

#print(chunk_text("testing chunk overlap"))