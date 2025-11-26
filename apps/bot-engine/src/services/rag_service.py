"""RAG service for document upload and retrieval."""

import os
from pathlib import Path
from typing import List, Optional, Any

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from supabase import create_client, Client
    from langchain_community.vectorstores import SupabaseVectorStore
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, UnstructuredWordDocumentLoader
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Try fallback to main langchain package
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.document_loaders import PyMuPDFLoader, TextLoader, UnstructuredWordDocumentLoader
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False

from whatsapp_bot_shared import get_logger

logger = get_logger(__name__)


class RAGService:
    """Service for RAG (Retrieval-Augmented Generation) operations."""

    def __init__(self, openai_api_key: Optional[str] = None, persist_directory: str = "./chroma_db"):
        """
        Initialize RAG service.

        Args:
            openai_api_key: OpenAI API key for embeddings
            persist_directory: Directory to persist ChromaDB data
        """
        self.backend = None
        self.vector_store = None
        self.collection = None
        self.enabled = False

        # Check dependencies first
        if not CHROMADB_AVAILABLE and not SUPABASE_AVAILABLE:
            logger.warning("No vector store (ChromaDB or Supabase) available. RAG functionality disabled.")
            return

        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain dependencies not available. RAG functionality disabled.")
            return

        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found")
            return

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=api_key,
        )

        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # Check for Supabase configuration first (preferred if configured)
        supabase_url = os.getenv("SUPABASE_URL")
        # Check SUPABASE_SERVICE_KEY first (primary), fallback to SUPABASE_SERVICE_ROLE_KEY
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if SUPABASE_AVAILABLE and supabase_url and supabase_key:
            try:
                logger.info("Initializing Supabase vector store...")
                self.supabase: Client = create_client(supabase_url, supabase_key)
                # Note: SupabaseVectorStore will handle user_id through metadata
                # We'll add user_id to each document's metadata when uploading
                self.vector_store = SupabaseVectorStore(
                    client=self.supabase,
                    embedding=self.embeddings,
                    table_name="documents",
                    query_name="match_documents",
                )
                self.backend = "supabase"
                self.enabled = True
                logger.info("RAG service initialized with Supabase")
                return
            except Exception as e:
                logger.error(f"Failed to initialize Supabase: {e}")

        # Fallback to ChromaDB
        if CHROMADB_AVAILABLE:
            try:
                logger.info("Initializing ChromaDB vector store...")
                self.persist_directory = persist_directory
                Path(persist_directory).mkdir(parents=True, exist_ok=True)

                self.client = chromadb.PersistentClient(
                    path=persist_directory,
                    settings=Settings(anonymized_telemetry=False),
                )

                # Get or create collection
                self.collection_name = "sales_documents"
                try:
                    self.collection = self.client.get_collection(name=self.collection_name)
                    logger.info(f"Loaded existing collection '{self.collection_name}'")
                except:
                    self.collection = self.client.create_collection(name=self.collection_name)
                    logger.info(f"Created new collection '{self.collection_name}'")
                
                self.backend = "chromadb"
                self.enabled = True
                logger.info("RAG service initialized with ChromaDB")
                return
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}")

        logger.warning("No vector store available. RAG functionality disabled.")
        self.enabled = False

    async def upload_document(self, file_path: str, user_id: Optional[str] = None) -> int:
        """
        Upload and process a single document.

        Args:
            file_path: Path to the document file
            user_id: Optional user ID to associate with the document

        Returns:
            Number of chunks created

        Raises:
            ValueError: If file format is not supported
        """
        if not self.enabled:
            logger.warning("RAG service disabled, cannot upload document")
            return 0

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = file_path_obj.suffix.lower()

        try:
            # Load document based on file type
            if extension == ".pdf":
                loader = PyMuPDFLoader(file_path)
            elif extension == ".txt":
                loader = TextLoader(file_path)
            elif extension in [".doc", ".docx"]:
                loader = UnstructuredWordDocumentLoader(file_path)
            else:
                raise ValueError(f"Unsupported file format: {extension}")

            logger.info(f"Loading document: {file_path_obj.name}")
            documents = loader.load()

            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split document into {len(chunks)} chunks")

            # Add metadata to chunks
            for i, chunk in enumerate(chunks):
                chunk.metadata["source"] = file_path_obj.name
                chunk.metadata["chunk_index"] = i
                if user_id:
                    chunk.metadata["user_id"] = user_id

            # Store in vector database
            if self.backend == "supabase":
                # For Supabase, the trigger will extract user_id from metadata
                self.vector_store.add_documents(chunks)
            
            elif self.backend == "chromadb":
                # Generate embeddings and store
                for i, chunk in enumerate(chunks):
                    # Generate embedding
                    embedding = self.embeddings.embed_query(chunk.page_content)

                    # Create unique ID
                    doc_id = f"{file_path_obj.stem}_{i}"

                    # Add to ChromaDB
                    self.collection.add(
                        ids=[doc_id],
                        embeddings=[embedding],
                        documents=[chunk.page_content],
                        metadatas=[chunk.metadata],
                    )

            logger.info(f"Successfully uploaded {len(chunks)} chunks from {file_path_obj.name}")
            return len(chunks)

        except Exception as e:
            logger.error(f"Error uploading document {file_path}: {e}")
            raise

    async def upload_documents(self, file_paths: List[str]) -> int:
        """
        Upload multiple documents.

        Args:
            file_paths: List of file paths

        Returns:
            Total number of chunks created
        """
        total_chunks = 0
        for file_path in file_paths:
            try:
                chunks = await self.upload_document(file_path)
                total_chunks += chunks
            except Exception as e:
                logger.error(f"Failed to upload {file_path}: {e}")
                continue

        logger.info(f"Uploaded {len(file_paths)} documents, total {total_chunks} chunks")
        return total_chunks

    async def retrieve_context(self, query: str, user_id: Optional[str] = None, k: int = 3) -> str:
        """
        Retrieve relevant context for a query, scoped to a specific user.

        Args:
            query: Search query
            user_id: User ID to filter documents (required for multi-tenant security)
            k: Number of top results to retrieve

        Returns:
            Concatenated context from top-k chunks
        """
        if not self.enabled:
            return ""

        try:
            contexts = []
            
            if self.backend == "supabase":
                # For Supabase, we need to use RPC call to match_documents with user_id filter
                if user_id:
                    # Generate query embedding
                    query_embedding = self.embeddings.embed_query(query)
                    
                    # Call match_documents RPC function with user_id filter
                    result = self.supabase.rpc(
                        "match_documents",
                        {
                            "query_embedding": query_embedding,
                            "match_count": k,
                            "filter": {},
                            "user_id_filter": user_id
                        }
                    ).execute()
                    
                    # Extract content from results
                    if result.data:
                        contexts = [doc["content"] for doc in result.data]
                else:
                    # Fallback: use similarity_search without filter (not recommended for multi-tenant)
                    logger.warning("retrieve_context called without user_id - using unfiltered search")
                    docs = self.vector_store.similarity_search(query, k=k)
                    contexts = [doc.page_content for doc in docs]
                
            elif self.backend == "chromadb":
                # Generate query embedding
                query_embedding = self.embeddings.embed_query(query)

                # Search in ChromaDB
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                )

                # Extract and format results
                if results["documents"] and len(results["documents"][0]) > 0:
                    contexts = results["documents"][0]

            if contexts:
                context_text = "\n\n---\n\n".join(contexts)
                logger.info(f"Retrieved {len(contexts)} relevant chunks for query (user_id: {user_id})")
                return context_text
            else:
                logger.info(f"No relevant context found for user {user_id}")
                return ""

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""

    def get_collection_stats(self, user_id: Optional[str] = None) -> dict:
        """
        Get statistics about the document collection for a specific user.

        Args:
            user_id: User ID to filter documents (required for multi-tenant)

        Returns:
            Dict with collection statistics
        """
        if not self.enabled:
            return {"total_chunks": 0, "backend": "none"}
            
        try:
            if self.backend == "supabase":
                # Use user-scoped RPC function for accurate count
                if user_id:
                    result = self.supabase.rpc(
                        "get_user_documents_count",
                        {"user_id_param": user_id}
                    ).execute()
                    count = result.data if result.data is not None else 0
                else:
                    # Fallback: query table directly (will be filtered by RLS)
                    result = self.supabase.table("documents").select("id", count="exact").execute()
                    count = result.count if hasattr(result, 'count') else 0
                
                return {
                    "total_chunks": count,
                    "backend": "supabase",
                    "status": "connected",
                    "user_id": user_id
                }
            elif self.backend == "chromadb":
                count = self.collection.count()
                return {
                    "total_chunks": count,
                    "collection_name": self.collection_name,
                    "backend": "chromadb"
                }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e), "backend": self.backend if self.backend else "unknown"}

    def clear_collection(self, user_id: Optional[str] = None) -> int:
        """
        Clear all documents from the collection for a specific user.

        Args:
            user_id: User ID to filter documents (required for multi-tenant security)

        Returns:
            Number of documents deleted
        """
        if not self.enabled:
            return 0

        try:
            if self.backend == "supabase":
                # Use user-scoped RPC function for safe deletion
                if user_id:
                    result = self.supabase.rpc(
                        "clear_user_documents",
                        {"user_id_param": user_id}
                    ).execute()
                    deleted_count = result.data if result.data is not None else 0
                    logger.info(f"Cleared {deleted_count} documents for user {user_id}")
                    return deleted_count
                else:
                    logger.error("user_id required for clear_collection in multi-tenant mode")
                    return 0
            elif self.backend == "chromadb":
                self.client.delete_collection(name=self.collection_name)
                self.collection = self.client.create_collection(name=self.collection_name)
                logger.info("ChromaDB collection cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise


# Global instance (will be initialized in app.py)
rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get the global RAG service instance."""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service
