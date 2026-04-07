import fitz

#for text and docs
def load_text(text: str)-> str:
    """
    text input
    """
    return text.strip()


#for url

from langchain_community.document_loaders import WebBaseLoader

def load_from_url(url: str) -> str:
   
    try:
        #breakpoint()
        loader = WebBaseLoader(url)
        # load() returns a list of LangChain Document objects
        docs = loader.load()
        
        if not docs:
            return ""
        #breakpoint()  
        # Extract text from the first document (or all of them)
        text = "\n".join([doc.page_content for doc in docs])
        
        # Clean extra spacing while preserving basic structure
        cleaned_text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])
        return cleaned_text

    except Exception as e:
        raise ValueError(f"Error loading URL: {str(e)}")


def load_pdf(file_path: str)-> str:
    """
    extract text from pdf using PyMuPDF
    """

    try:
        doc=fitz.open(file_path)
        text=""

        for page in doc:
            text+=page.get_text()
        doc.close()

        cleaned_text = " ".join(text.split())
        return cleaned_text
    except Exception as e:
        raise ValueError(f"Error loading PDF: {str(e)}")
    

