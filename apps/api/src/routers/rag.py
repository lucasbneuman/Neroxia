"""RAG document management router."""

import os
import sys
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from neroxia_shared import get_logger

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
async def upload_documents(
    files: List[UploadFile] = File(..., description="One or more files to upload"),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload one or more documents for RAG processing.

    Supports PDF, TXT, DOC, and DOCX files.
    Documents will be processed and added to the knowledge base.

    Note: This endpoint receives files via multipart/form-data with field name 'files'
    """
    try:
        rag_service = get_rag_service()

        if not rag_service.enabled:
            raise HTTPException(
                status_code=503,
                detail="RAG service is not available. ChromaDB may not be installed."
            )

        if not files:
            raise HTTPException(
                status_code=400,
                detail="No files provided. Please upload at least one file."
            )

        allowed_extensions = [".pdf", ".txt", ".doc", ".docx"]
        total_chunks = 0
        uploaded_files = []

        for file in files:
            # Validate file extension
            file_ext = Path(file.filename).suffix.lower()

            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type for {file.filename}. Allowed: {', '.join(allowed_extensions)}"
                )

            # Create user-specific directory
            user_id = current_user.get("id")
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID required")
                
            user_upload_dir = UPLOAD_DIR / str(user_id)
            user_upload_dir.mkdir(parents=True, exist_ok=True)

            # Save uploaded file
            file_path = user_upload_dir / file.filename

            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            logger.info(f"Saved uploaded file: {file.filename} ({len(content)} bytes) for user {user_id}")

            # Process with RAG service
            chunks_created = await rag_service.upload_document(str(file_path), user_id=user_id)

            logger.info(f"Processed {file.filename}: {chunks_created} chunks created")

            uploaded_files.append(file.filename)
            total_chunks += chunks_created

        return {
            "status": "success",
            "uploaded": len(uploaded_files),
            "files": uploaded_files,
            "total_chunks": total_chunks,
            "message": f"Successfully uploaded {len(uploaded_files)} file(s) with {total_chunks} total chunks"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading documents: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload documents: {str(e)}"
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
        
        user_id = current_user.get("id")
        if not user_id:
            return []
            
        user_upload_dir = UPLOAD_DIR / str(user_id)
        if not user_upload_dir.exists():
            return []
        
        for file_path in user_upload_dir.iterdir():
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
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID required")
            
        file_path = UPLOAD_DIR / str(user_id) / filename
        
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
    Get RAG collection statistics for the authenticated user.
    
    Returns information about the number of document chunks in the vector database.
    """
    try:
        rag_service = get_rag_service()
        
        if not rag_service.enabled:
            return {
                "enabled": False,
                "message": "RAG service is not available"
            }
        
        # Extract user_id from JWT token for multi-tenant security
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid user token: missing user ID"
            )
        
        stats = rag_service.get_collection_stats(user_id=user_id)
        
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


@router.delete("/clear")
async def clear_collection(
    current_user: dict = Depends(get_current_user)
):
    """
    Clear all documents from the RAG collection for the authenticated user.
    
    WARNING: This will remove all YOUR document chunks from the vector database.
    Other users' documents will not be affected.
    """
    try:
        rag_service = get_rag_service()
        
        if not rag_service.enabled:
            raise HTTPException(
                status_code=503,
                detail="RAG service is not available"
            )
        
        # Extract user_id from JWT token for multi-tenant security
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid user token: missing user ID"
            )
        
        deleted_count = rag_service.clear_collection(user_id=user_id)
        
        logger.info(f"User {user_id} cleared {deleted_count} documents from RAG collection")
        
        return {
            "status": "success",
            "message": f"RAG collection cleared successfully ({deleted_count} documents deleted)",
            "deleted_count": deleted_count
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing collection: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear collection: {str(e)}"
        )
