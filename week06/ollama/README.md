# Ollama Embeddings Demo

This is a simple Python program that demonstrates how to use Ollama embeddings.

## Prerequisites

- Python 3.6+
- Ollama installed and running locally
- Required Python packages: `requests`, `numpy`

## Installation

1. Make sure Ollama is installed and running on your machine
   - Follow the installation instructions at [Ollama's official website](https://ollama.ai/)
   - Start the Ollama service

2. Pull the required embedding model:
   ```
   ollama pull jina/jina-embeddings-v2-base-en:latest
   ```

3. Install the required Python packages:
   ```
   pip install requests numpy
   ```

## Usage

Run the program with:

```
python ollama_embeddings.py
```

## What the Program Does

This program demonstrates:

1. How to connect to the Ollama API to generate embeddings
2. How to convert text into vector embeddings
3. How to compare the semantic similarity between different texts using cosine similarity

The program generates embeddings for four example texts and compares their similarities to show how semantically related texts have higher similarity scores.

## How It Works

- The program sends requests to the Ollama API endpoint at `http://localhost:11434/api/embed`
- It uses the `jina/jina-embeddings-v2-base-en:latest` model by default for generating embeddings
- It converts each text into a high-dimensional vector (embedding)
- It calculates the cosine similarity between pairs of embeddings
- Similar texts will have a higher similarity score (closer to 1)
- Dissimilar texts will have a lower similarity score (closer to 0)

## Extending the Program

You can modify the program to:
- Use different Ollama models by changing the `model` parameter
- Add your own texts to compare
- Implement more advanced applications like text clustering or document retrieval
