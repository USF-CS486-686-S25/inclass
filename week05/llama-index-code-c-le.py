import os
import sys
from pathlib import Path
import requests
import json
from typing import List, Optional

from rich import print
from rich.pretty import Pretty
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex
from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document
from llama_index.core.node_parser import CodeSplitter
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.bridge.pydantic import Field, PrivateAttr

# Create a custom embedding class for Ollama
class OllamaEmbedding(BaseEmbedding):
    """Ollama embedding model.
    
    Uses Ollama's API to generate embeddings.
    """
    model_name: str = Field(default="jina/jina-embeddings-v2-base-en:latest", description="Name of the Ollama embedding model")
    _base_url: str = PrivateAttr(default="http://localhost:11434")
    
    def __init__(
        self,
        model_name: str = "jina/jina-embeddings-v2-base-en:latest",
        base_url: str = "http://localhost:11434",
        embed_batch_size: int = 10,
        **kwargs
    ):
        """Initialize Ollama embedding model."""
        super().__init__(embed_batch_size=embed_batch_size, **kwargs)
        self._base_url = base_url.rstrip("/")
        
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text using Ollama API."""
        url = f"{self._base_url}/api/embed"
        payload = {
            "model": self.model_name,
            "input": text
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            # Get the embeddings from the response
            embeddings = response.json().get("embeddings", [])
            
            # Handle the case where embeddings is a list of lists
            if embeddings and isinstance(embeddings, list):
                if len(embeddings) == 1:
                    # If we have a single embedding (list of lists), return the first one
                    return embeddings[0]
                elif embeddings and isinstance(embeddings[0], list):
                    # If we have multiple embeddings, just return the first one for now
                    return embeddings[0]
                else:
                    # If it's already a flat list, return it
                    return embeddings
            
            # Fallback
            return embeddings
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return a zero vector as fallback (adjust dimension as needed)
            return [0.0] * 384  # Typical embedding dimension
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for a query."""
        return self._get_embedding(query)
    
    def _get_text_embedding(self, text: str) -> List[float]:
        """Get embedding for a text."""
        return self._get_embedding(text)
    
    async def _aget_query_embedding(self, query: str) -> List[float]:
        """Get embedding for a query asynchronously."""
        return self._get_embedding(query)
    
    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Get embedding for a text asynchronously."""
        return self._get_embedding(text)
        
    def _get_text_embedding_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a batch of texts."""
        embeddings = []
        for text in texts:
            embeddings.append(self._get_embedding(text))
        return embeddings

# Set up Ollama embedding model
embed_model = OllamaEmbedding(
    #model_name="nomic-embed-text",
    model_name="jina/jina-embeddings-v2-base-en:latest",
    base_url="http://localhost:11434",  # Default Ollama server URL
)

# Configure LlamaIndex to use Ollama embeddings
Settings.embed_model = embed_model

# Create a text splitter instance (using SentenceSplitter instead of CodeSplitter to avoid tree-sitter dependency)
text_splitter = SentenceSplitter(
    chunk_size=512,
    chunk_overlap=50
)

# Create a code splitter instance
code_splitter = CodeSplitter(
    language="c",  # Default language
    chunk_lines=30,    # Number of lines per chunk
    chunk_lines_overlap=5,  # Number of overlapping lines between chunks
    max_chars=512,    # Maximum characters per chunk
)

# Load documents
reader = SimpleDirectoryReader(input_dir="xv6-riscv",
                               recursive=True,
                               exclude_hidden=True,
                               required_exts=[".c", ".h"])
                                
documents = reader.load_data()

print(f"Loaded {len(documents)} documents")

#print("=== DOCUMENTS ===")
#print(Pretty(documents))    

# Process documents with SentenceSplitter
#nodes = text_splitter.get_nodes_from_documents(documents)
#print(f"Created {len(nodes)} text chunks")

nodes = code_splitter.get_nodes_from_documents(documents)
print(f"Created {len(nodes)} code chunks")

# Create index from the processed nodes
index = VectorStoreIndex(nodes)

query_engine = index.as_query_engine(response_mode="tree_summarize",
                                   verbose=True,)

response = query_engine.query("What files, functions, and lines of code are responsible for process creation?")

print("=== RESPONSE DETAILS ===")
print(response)

print("=== RESPONSE ===")
print(response.response)

print("=== EMBEDDING MODEL ===")
print(Settings.embed_model)

print("=== LLM ===")
print(Settings.llm)