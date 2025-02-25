#!/usr/bin/env python3

import sys
import re
import math
from typing import List, Dict, Tuple

class VectorDB:
    def __init__(self):
        self.entries: List[Tuple[str, List[float]]] = []  # [(text, embedding)]
    
    def add(self, text: str, embedding: List[float]):
        """Add a text and its embedding to the database."""
        # Normalize the embedding vector
        norm = math.sqrt(sum(x*x for x in embedding))
        if norm > 0:
            normalized_emb = [x/norm for x in embedding]
            self.entries.append((text, normalized_emb))
    
    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = sum(a*b for a, b in zip(v1, v2))
        return dot_product  # vectors are already normalized
    
    def query(self, query_emb: List[float], top_k: int = 3) -> List[Tuple[str, float]]:
        """Find top_k most similar entries to the query embedding."""
        # Normalize query vector
        norm = math.sqrt(sum(x*x for x in query_emb))
        if norm == 0:
            return []
        normalized_query = [x/norm for x in query_emb]
        
        # Compute similarities
        similarities = [
            (text, self.cosine_similarity(normalized_query, emb))
            for text, emb in self.entries
        ]
        
        # Sort by similarity (highest first) and return top_k
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]

def create_vocabulary(text: str) -> Dict[str, int]:
    """Create a vocabulary mapping from the entire text."""
    # Convert to lowercase and split into words
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    words = cleaned_text.split()
    
    # Create vocabulary (unique words)
    vocab = sorted(set(words))
    
    # Create word to index mapping
    word_to_idx = {word: idx for idx, word in enumerate(vocab)}
    
    return word_to_idx

def chunk_text(text: str, chunk_size: int = 512) -> List[str]:
    """Split text into chunks of approximately chunk_size bytes, preserving word boundaries."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        # Calculate size including space
        word_size = len(word) + 1  # +1 for the space
        
        if current_size + word_size > chunk_size and current_chunk:
            # If adding this word would exceed chunk_size, store current chunk
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            # Add word to current chunk
            current_chunk.append(word)
            current_size += word_size
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def create_bow_embedding(text: str, vocabulary: Dict[str, int]) -> List[float]:
    """Create a bag-of-words embedding for the text using the vocabulary."""
    # Initialize embedding vector with zeros
    embedding = [0.0] * len(vocabulary)
    
    # Clean text
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    words = cleaned_text.split()
    
    # Count words
    for word in words:
        if word in vocabulary:
            embedding[vocabulary[word]] += 1.0
            
    return embedding

def main():
    # Check if filename was provided
    if len(sys.argv) != 2:
        print("Usage: python vocab.py filename")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        # Read text from file
        with open(filename, 'r') as f:
            text = f.read()
        
        # First, create global vocabulary
        global_vocab = create_vocabulary(text)
        print("\nGlobal Vocabulary:")
        print("=" * 50)
        for word, idx in global_vocab.items():
            print(f"{word}: {idx}")
        print(f"\nTotal vocabulary size: {len(global_vocab)}")
        
        # Initialize vector database
        db = VectorDB()
        
        # Split text into chunks and process each chunk
        chunks = chunk_text(text)
        print(f"\nProcessing text in {len(chunks)} chunks (~512 bytes each):")
        print("=" * 50)
        
        # Process each chunk
        for i, chunk in enumerate(chunks, 1):
            # Create embedding for chunk
            embedding = create_bow_embedding(chunk, global_vocab)
            
            # Add to vector database
            db.add(chunk, embedding)
            
            print(f"\nChunk {i} (size: {len(chunk)} bytes):")
            print("-" * 20)
            print("Text:", chunk[:100] + "..." if len(chunk) > 100 else chunk)
            
        # Demonstrate vector database query
        print("\nVector Database Demo:")
        print("=" * 50)
        print("Querying with first chunk as example:")
        test_query = "file descriptor"
        if chunks:
            query_emb = create_bow_embedding(test_query, global_vocab)
            results = db.query(query_emb, top_k=2)
            print("\nTop 2 similar chunks:")
            for text, similarity in results:
                print(f"\nSimilarity: {similarity:.4f}")
                print(f"Text: {text[:500]}...")
            
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
