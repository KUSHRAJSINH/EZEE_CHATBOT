import uuid
import tempfile
import os
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from model_schema.schemas import UploadResponse
from services.loader import load_text, load_pdf, load_from_url
from services.chunking import chunk_text
from db_store.vector_store import get_vector_store

router = APIRouter(tags=["upload"])

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    type: Literal["text", "url", "pdf"] = Form(..., description="Type of content being uploaded"),
    content: Optional[str] = Form(None, description="Raw text or URL string if type is 'text' or 'url'"),
    file: Optional[UploadFile] = File(None, description="PDF file to upload if type is 'pdf'")
) -> UploadResponse:
    """
    Ingest content (text, URL, or PDF) into a new isolated ChromaDB collection.
    """
    # ── Step 1: Load content ─────────────────────────────────────────────────
    try:
        #breakpoint()
        if type == "text":
            if not content:
                raise HTTPException(status_code=400, detail="Missing 'content' field for text upload.")
            raw_text = load_text(content)

        elif type == "url":
            if not content:
                raise HTTPException(status_code=400, detail="Missing 'content' field for URL upload.")
            raw_text = load_from_url(content)

        elif type == "pdf":
            if not file:
                raise HTTPException(status_code=400, detail="Missing 'file' upload for PDF type.")
            
            # Write the uploaded file to a temporary location so PyMuPDF can read it
            pdf_bytes = await file.read()
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name
                
            try:

                raw_text = load_pdf(tmp_path)
            finally:
                os.remove(tmp_path)

        else:
            raise HTTPException(status_code=400, detail="Unsupported content type.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Content loading failed: {str(e)}")

    if not raw_text or not raw_text.strip():
        raise HTTPException(status_code=422, detail="Extracted content is empty.")

    # ── Step 2: Chunk ────────────────────────────────────────────────────────
    chunks = chunk_text(raw_text)
    if not chunks:
        raise HTTPException(status_code=422, detail="No chunks produced from content.")

    # ── Step 3: Embed + Store ────────────────────────────────────────────────
    bot_id = str(uuid.uuid4())

    try:
        vector_store = get_vector_store(bot_id)
        # Generate a unique ID per chunk so they don't overwrite each other
        chunk_ids = [f"{bot_id}_{i}" for i in range(len(chunks))]
        vector_store.add_texts(texts=chunks, ids=chunk_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector store error: {str(e)}")

    return UploadResponse(bot_id=bot_id)
