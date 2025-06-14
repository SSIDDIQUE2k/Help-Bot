# Helper functions for data processing, e.g., HTML cleaning 

import chromadb
from langchain_community.embeddings import sentence_transformer

# --- Vector Store (Chroma) ---
CHROMA_PATH = "chroma_db"
_chroma_client = None

def get_chroma_client():
    """Returns a persistent ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        # Using a persistent client that saves to disk
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _chroma_client

# --- Embedding Function ---
_embedding_function = None

def get_embedding_function():
    """
    Returns a SentenceTransformer embedding model.
    Downloads the model on first use.
    """
    global _embedding_function
    if _embedding_function is None:
        model_name = "all-MiniLM-L6-v2"
        print(f"Loading embedding model '{model_name}'... (This may take a moment on first run)")
        _embedding_function = sentence_transformer.SentenceTransformerEmbeddings(
            model_name=model_name
        )
        print("Embedding model loaded.")
    return _embedding_function 