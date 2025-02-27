#!/usr/bin/env python3
"""
A simple demonstration of using Ollama embeddings.
This program shows how to:
1. Connect to the Ollama API
2. Generate embeddings for text
3. Compare similarity between different text embeddings
"""

import requests
import numpy as np
from typing import List, Dict, Any
import json

# Ollama API endpoint for embeddings
OLLAMA_API_URL = "http://localhost:11434/api/embed"

def get_embedding(text: str, model: str = "jina/jina-embeddings-v2-base-en:latest") -> List[float]:
    """
    Get embeddings for a piece of text using Ollama API.
    
    Args:
        text: The input text to generate embeddings for
        model: The model to use for generating embeddings
        
    Returns:
        A list of floats representing the embedding vector
    """
    payload = {
        "model": model,
        "input": text
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        result = response.json()
        
        # Debug information
        if "embeddings" not in result:
            print(f"Warning: API response does not contain 'embeddings' key. Response: {result}")
            return []
            
        return result["embeddings"]
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {e}")
        print("Make sure Ollama is running and the model is available.")
        print("You may need to pull the model first with: ollama pull jina/jina-embeddings-v2-base-en:latest")
        return []

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score between 0 and 1
    """
    # Convert to numpy arrays for easier calculation
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    # Ensure vectors are flattened to 1D
    vec1 = vec1.flatten()
    vec2 = vec2.flatten()
    
    # Calculate cosine similarity
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    # Avoid division by zero
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0
    
    return dot_product / (norm_vec1 * norm_vec2)

def main():
    """Main function to demonstrate Ollama embeddings."""
    print("Ollama Embeddings Demonstration")
    print("===============================")
    
    # Example texts to compare
    texts = [
        "I love machine learning and artificial intelligence",
        "Deep learning models have transformed NLP",
        "The weather is nice today",
        "It's a beautiful sunny day outside"
    ]
    
    print("\nGenerating embeddings for sample texts...")
    
    # Generate embeddings for each text
    embeddings = []
    for i, text in enumerate(texts):
        print(f"Text {i+1}: {text}")
        embedding = get_embedding(text)
        if embedding:
            embeddings.append(embedding)
            print(f"  ✓ Generated embedding with {len(embedding)} dimensions")
        else:
            print("  ✗ Failed to generate embedding")
    
    # Compare similarities between all pairs of texts
    if len(embeddings) > 1:
        print("\nComparing similarities between texts:")
        for i in range(len(texts)):
            for j in range(i+1, len(texts)):
                if i < len(embeddings) and j < len(embeddings):
                    # Check if embeddings are not empty
                    if embeddings[i] and embeddings[j]:
                        similarity = cosine_similarity(embeddings[i], embeddings[j])
                        print(f"Similarity between Text {i+1} and Text {j+1}: {similarity:.4f}")
    elif len(embeddings) == 0:
        print("\nNo embeddings were generated. Please check that Ollama is running correctly.")
        print("You may need to pull the model first with: ollama pull jina/jina-embeddings-v2-base-en:latest")
    else:
        print("\nOnly one embedding was generated. Need at least two for comparison.")
    
    print("\nDemonstration complete!")

if __name__ == "__main__":
    main()