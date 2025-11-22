"""RAG document management router."""

import os
import sys
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel

from whatsapp_bot_shared import get_logger

# Add bot-engine to Python path
bot_engine_path = Path(__file__).parent.parent.parent.parent / "bot-engine" / "src"
if str(bot_engine_path) not in sys.path:
    sys.path.insert(0, str(bot_engine_path))

# Import bot-engine services
from services.rag_service import get_rag_service

from .auth import get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])

# Directory for uploaded files
UPLOAD_DIR = Path("./rag_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class FileInfo(BaseModel):
    """File information."""
    filename: str
    size: int
    uploaded_at: str


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a document for RAG processing.
    
    Supports PDF, TXT, DOC, and DOCX files.
    The document will be processed and added to the knowledge base.
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        allowed_extensions = [".pdf", ".txt", ".doc", ".docx"]
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved uploaded file: {file.filename} ({len(content)} bytes)")
        
        # Process with RAG service
        rag_service = get_rag_service()
        
        if not rag_service.enabled:
            raise HTTPException(
                status_code=503,
                detail="RAG service is not available. ChromaDB may not be installed."
            )
        
        chunks_created = await rag_service.upload_document(str(file_path))
        
        logger.info(f"Processed {file.filename}: {chunks_created} chunks created")
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_created": chunks_created,
            "message": f"Document uploaded and processed successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get("/files")
async def list_files(
    current_user: dict = Depends(get_current_user)
) -> List[FileInfo]:
    """
    List all uploaded RAG documents.
    
    Returns information about files in the upload directory.
    """
    try:
        files = []
        
        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append(FileInfo(
                    filename=file_path.name,
                    size=stat.st_size,
                    uploaded_at=str(stat.st_mtime)
                ))
        
        logger.info(f"Listed {len(files)} RAG files")
        return files
    
    except Exception as e:
        logger.error(f"Error listing files: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list files: {str(e)}"
        )


@router.delete("/files/{filename}")
async def delete_file(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an uploaded RAG document.
    
    Note: This only deletes the file from disk, not from the vector database.
    To fully remove, you may need to clear and rebuild the collection.
    """
    try:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}"
            )
        
        # Delete file
        file_path.unlink()
        
        logger.info(f"Deleted file: {filename}")
        
        return {
            "status": "success",
            "message": f"File {filename} deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )


@router.get("/stats")
async def get_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get RAG collection statistics.
    
    Returns information about the number of document chunks in the vector database.
    """
    try:
        rag_service = get_rag_service()
        
        if not rag_service.enabled:
            return {
                "enabled": False,
                "message": "RAG service is not available"
            }
        
        stats = rag_service.get_collection_stats()
        
        return {
            "enabled": True,
            **stats
        }
    
    except Exception as e:
        logger.error(f"Error getting RAG stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get RAG stats: {str(e)}"
        )


@router.post("/clear")
async def clear_collection(
    current_user: dict = Depends(get_current_user)
):
    """
    Clear all documents from the RAG collection.
    
    WARNING: This will remove all document chunks from the vector database.
    """
    try:
        rag_service = get_rag_service()
        
        if not rag_service.enabled:
            raise HTTPException(
                status_code=503,
                detail="RAG service is not available"
            )
        
        rag_service.clear_collection()
        
        logger.info("Cleared RAG collection")
        
        return {
            "status": "success",
            "message": "RAG collection cleared successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing collection: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear collection: {str(e)}"
        )
