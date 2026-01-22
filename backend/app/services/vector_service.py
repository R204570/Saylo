"""
ChromaDB vector database service for semantic search.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from loguru import logger
from app.config import settings
from app.services.ollama_service import ollama_service
import os


class VectorService:
    """Service for vector storage and retrieval using ChromaDB."""
    
    def __init__(self):
        # Ensure ChromaDB directory exists
        os.makedirs(settings.chromadb_path, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=settings.chromadb_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        logger.info(f"ChromaDB initialized at {settings.chromadb_path}")
    
    def get_or_create_collection(self, collection_name: str):
        """
        Get or create a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            ChromaDB collection
        """
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            return collection
        except Exception as e:
            logger.error(f"Error getting/creating collection: {e}")
            raise
    
    async def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: List of metadata dicts
            ids: Optional list of document IDs
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Generate embeddings using Ollama
            embeddings = await ollama_service.generate_embeddings(documents)
            
            # Generate IDs if not provided
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(documents))]
            
            # Add to collection
            collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to collection '{collection_name}'")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    async def query_documents(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 3,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query documents from a collection.
        
        Args:
            collection_name: Name of the collection
            query_text: Query text
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Query results with documents, metadatas, and distances
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Generate query embedding
            query_embeddings = await ollama_service.generate_embeddings([query_text])
            
            # Query collection
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            raise
    
    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of the collection to delete
        """
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise
    
    def list_collections(self) -> List[str]:
        """
        List all collections.
        
        Returns:
            List of collection names
        """
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            raise
    
    async def get_relevant_context(
        self,
        collection_name: str,
        query: str,
        max_chunks: int = 3
    ) -> str:
        """
        Get relevant context for a query.
        
        Args:
            collection_name: Name of the collection
            query: Query text
            max_chunks: Maximum number of chunks to retrieve
            
        Returns:
            Concatenated relevant context
        """
        try:
            results = await self.query_documents(
                collection_name=collection_name,
                query_text=query,
                n_results=max_chunks
            )
            
            if not results or not results.get("documents"):
                return "No relevant context found."
            
            # Concatenate documents
            documents = results["documents"][0]  # First query result
            context = "\n\n".join(documents)
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return "Error retrieving context."


# Global instance
vector_service = VectorService()
