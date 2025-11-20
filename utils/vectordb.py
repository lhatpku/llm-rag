import os

# Disable ChromaDB telemetry BEFORE importing chromadb to avoid "capture() takes 1 positional argument but 3 were given" warnings
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from utils.paths import DATA_DIR

load_dotenv()

class VectorDB:
    """
    A simple vector database wrapper using ChromaDB with HuggingFace embeddings.
    """

    def __init__(self, collection_name: str = None, embedding_model: str = None, default_threshold: float = 0.5):
        """
        Initialize the vector database.

        Args:
            collection_name: Name of the ChromaDB collection
            embedding_model: HuggingFace model name for embeddings
            default_threshold: Default similarity threshold for search (can be overridden per query)
        """
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        self.default_threshold = default_threshold

        # Initialize ChromaDB client
        os.makedirs(DATA_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(path=DATA_DIR)

        # Load embedding model
        print(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "RAG document collection","hnsw:space": "cosine",
                "hnsw:batch_size": 10000},
        )

        print(f"Vector database initialized with collection: {self.collection_name}")

    def chunk_text(self, text: str, chunk_size: int = 400, chunk_overlap: int = 100) -> List[str]:
        """
        Simple text chunking by splitting on spaces and grouping into chunks.

        Args:
            text: Input text to chunk
            chunk_size: Approximate number of characters per chunk
            chunk_overlap: The number of characters overlapped between chunks

        Returns:
            List of text chunks
        """
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )   

        return text_splitter.split_text(text)
    

    def add_documents(self, documents: List) -> None:
        """
        Add documents to the vector database.
        - Use self.chunk_text() to split each document into chunks
        - Create unique IDs for each chunk (e.g., "doc_0_chunk_0")
        - Store the embeddings, documents and IDs in your vector database
        Args:
            documents: List of documents
        """
 
        model = self.embedding_model

        doc_id = 0

        for document in documents:

            print(f'Processing Document {doc_id+1}/{len(documents)}')

            chunked_publication = self.chunk_text(document)
            embeddings = model.encode(chunked_publication)
            chunk_ids = list(range(len(chunked_publication)))
            ids = [f"doc_{doc_id}_chunk_{id}" for id in chunk_ids]
            self.collection.add(
                embeddings=embeddings,
                ids=ids,
                documents=chunked_publication,
            )
            doc_id += 1


    def search(self, query: str, n_results: int = 3, threshold: float = 0.5,) -> Dict[str, Any]:
        """
        Search for similar documents in the vector database.

        Args:
            query: Search query
            n_results: Number of results to return
            threshold (float): Threshold for the cosine distance
        Returns:
            Dictionary containing search results with keys: 'documents', 'metadatas', 'distances', 'ids'
        """

        relevant_results = {
            "ids": [],
            "documents": [],
            "distances": []
        }

        query_embedding = self.embedding_model.encode([query])[0] 

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "distances"],
        )

        if len(results) == 0:
            print('Cannot find relevant documents.')
            
            return {
                "documents": [],
                "distances": [],
                "ids": [],
            }

        keep_item = [False] * len(results["ids"][0])
        for i, distance in enumerate(results["distances"][0]):
            if distance < threshold:
                keep_item[i] = True

        for i, keep in enumerate(keep_item):
            if keep:
                relevant_results["ids"].append(results["ids"][0][i])
                relevant_results["documents"].append(results["documents"][0][i])
                relevant_results["distances"].append(results["distances"][0][i])
    
        return relevant_results

