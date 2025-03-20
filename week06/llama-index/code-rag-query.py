#!/usr/bin/env python3
import json
import sys
import argparse
import os
from typing import List, Dict, Any, Optional

def check_requirements(model: str) -> bool:
    """
    Check if the required packages for the specified model are installed.
    Print installation instructions if they are not.
    
    Args:
        model: The model to check requirements for
        
    Returns:
        True if all requirements are met, False otherwise
    """
    try:
        import llama_index
    except ImportError:
        print("Error: LlamaIndex is not installed.")
        print("Please install it with: pip install llama-index")
        return False

    if model == "gpt-3.5":
        try:
            from llama_index.llms.openai import OpenAI
        except ImportError:
            print("Error: OpenAI module for LlamaIndex is not installed.")
            print("Please install it with: pip install llama-index-llms-openai")
            return False
    
    if model == "claude-3.7":
        try:
            from llama_index.llms.anthropic import Anthropic
        except ImportError:
            print("Error: Anthropic module for LlamaIndex is not installed.")
            print("Please install it with: pip install llama-index-llms-anthropic")
            return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Code RAG Query - Use code chunks with LLMs to answer user questions")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query an LLM with code chunks and a question")
    query_parser.add_argument("model", choices=["gpt-3.5", "claude-3.7"], help="LLM to use for the query")
    query_parser.add_argument("chunks_file", help="JSON file containing code chunks")
    query_parser.add_argument("question", help="Question to ask the LLM")
    
    args = parser.parse_args()
    
    if args.command == "query":
        # Check for required packages before proceeding
        if check_requirements(args.model):
            query_llm(args.model, args.chunks_file, args.question)
    else:
        parser.print_help()

def query_llm(model: str, chunks_file: str, question: str) -> None:
    """
    Load code chunks, create a prompt, query the specified language model, and print the response.
    
    Args:
        model: The language model to use (gpt-3.5 or claude-3.7)
        chunks_file: Path to a JSON file containing code chunks
        question: The question to ask the language model about the code
    """
    # 1. Load the code chunks from the JSON file
    chunks = load_code_chunks(chunks_file)
    if not chunks:
        sys.exit(1)
    
    # 2. Create the prompt with code chunks and question
    prompt = create_prompt(chunks, question)
    
    # 3. Query the appropriate model and get the response
    response = None
    if model == "gpt-3.5":
        response = query_gpt(prompt)
    elif model == "claude-3.7":
        response = query_claude(prompt)
    
    if response:
        # 4. Print the response
        print(response)
    else:
        sys.exit(1)

def load_code_chunks(chunks_file: str) -> Optional[List[Dict[str, Any]]]:
    """
    Load code chunks from a JSON file.
    
    Args:
        chunks_file: Path to the JSON file containing code chunks
    
    Returns:
        A list of code chunk dictionaries, or None if there was an error
    """
    try:
        with open(chunks_file, 'r') as f:
            chunks = json.load(f)
        return chunks
    except FileNotFoundError:
        print(f"Error: Chunks file '{chunks_file}' not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Chunks file '{chunks_file}' is not valid JSON")
        return None
    except Exception as e:
        print(f"Error loading chunks file: {str(e)}")
        return None

def create_prompt(chunks: List[Dict[str, Any]], question: str) -> str:
    """
    Create a prompt that includes the code chunks and the user's question.
    
    Args:
        chunks: A list of code chunk dictionaries
        question: The question to ask about the code
    
    Returns:
        A prompt string that includes the code chunks and question
    """
    prompt = "I will provide you with code chunks and a question. Please analyze the code and answer the question based on the provided code.\n\n"
    prompt += "Code Chunks:\n\n"
    
    for i, chunk in enumerate(chunks):
        prompt += f"Chunk {i+1} (File: {chunk['filename']}, Lines {chunk['start_line']}-{chunk['end_line']}):\n"
        prompt += f"```\n{chunk['content']}\n```\n\n"
    
    prompt += f"Question: {question}\n\n"
    prompt += "Please provide a detailed answer to the question based only on the code chunks provided."
    
    return prompt

def query_gpt(prompt: str) -> Optional[str]:
    """
    Query the OpenAI GPT-3.5 API using LlamaIndex.
    
    Args:
        prompt: The prompt to send to the API
    
    Returns:
        The API response as a string, or None if there was an error
    """
    # Import here to avoid errors if the package isn't installed
    from llama_index.llms.openai import OpenAI
    
    # This requires the OpenAI API key to be set in the environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return None
    
    try:
        # Initialize the OpenAI LLM through LlamaIndex
        llm = OpenAI(model="gpt-3.5-turbo", api_key=api_key)
        
        # Complete the prompt
        response = llm.complete(prompt)
        
        return str(response)
    except Exception as e:
        print(f"Error querying GPT-3.5: {str(e)}")
        return None

def query_claude(prompt: str) -> Optional[str]:
    """
    Query the Anthropic Claude-3.7 API using LlamaIndex.
    
    Args:
        prompt: The prompt to send to the API
    
    Returns:
        The API response as a string, or None if there was an error
    """
    # Import here to avoid errors if the package isn't installed
    from llama_index.llms.anthropic import Anthropic
    
    # This requires the Anthropic API key to be set in the environment
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set")
        return None
    
    try:
        # Initialize the Claude LLM through LlamaIndex
        llm = Anthropic(model="claude-3-sonnet-20240229", api_key=api_key)
        
        # Complete the prompt
        response = llm.complete(prompt)
        
        return str(response)
    except Exception as e:
        print(f"Error querying Claude-3.7: {str(e)}")
        return None

if __name__ == "__main__":
    main()