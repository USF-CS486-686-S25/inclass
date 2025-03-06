#!/usr/bin/env python3
"""
Test script for the enhanced CodeSplitter with file and line number metadata.
This script takes a C source file as a command line argument and processes it
using the enhanced CodeSplitter.

Usage:
    python code-meta-test.py <path_to_c_file>

Example:
    python code-meta-test.py /path/to/source/file.c
"""

import os
import sys
from pathlib import Path

# Import the enhanced CodeSplitter
try:
    # Using importlib to handle the hyphen in the filename
    import importlib.util
    spec = importlib.util.spec_from_file_location("code_meta", "code-meta.py")
    code_meta = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(code_meta)
    CodeSplitter = code_meta.CodeSplitter
    
    from llama_index.core.schema import Document
    from llama_index.core import VectorStoreIndex
    from tree_sitter import Language, Parser
except ImportError as e:
    print(f"Error: {e}")
    print("Please ensure you have the required packages installed:")
    print("pip install llama-index tree-sitter tree-sitter-languages")
    sys.exit(1)

def setup_tree_sitter():
    """
    Set up tree-sitter for C language parser.
    """
    try:
        # Directory to store tree-sitter languages
        languages_dir = Path("./tree-sitter-langs")
        languages_dir.mkdir(exist_ok=True)
        
        # Path to the built language library
        library_path = languages_dir / "languages.so"
        
        # Check if we need to build the language
        if not library_path.exists():
            print("Setting up tree-sitter C parser...")
            
            # Clone the C grammar repository if it doesn't exist
            c_repo_path = languages_dir / "tree-sitter-c"
            if not c_repo_path.exists():
                os.system(f"git clone https://github.com/tree-sitter/tree-sitter-c {c_repo_path}")
            
            # Build the language library
            Language.build_library(
                str(library_path),
                [str(c_repo_path)]
            )
            print("Tree-sitter C parser setup complete!")
        
        # Set environment variable for tree-sitter to find the languages
        os.environ["LLAMA_INDEX_TREE_SITTER_LIB_PATH"] = str(library_path)
        
        # Load the C language to verify it works
        C_LANGUAGE = Language(str(library_path), 'c')
        print("Successfully loaded C language parser")
        return C_LANGUAGE, str(library_path)
    except Exception as e:
        print(f"Error setting up tree-sitter: {e}")
        import traceback
        traceback.print_exc()
        return None, ""

def process_c_file_with_enhanced_splitter(file_path):
    """Process a C file using the enhanced CodeSplitter with file path metadata."""
    try:
        # Check if the file exists
        if not os.path.isfile(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            return None, None
        
        # Get the absolute path and base directory
        abs_path = os.path.abspath(file_path)
        base_dir = os.path.dirname(abs_path)
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            c_code = f.read()
        
        print(f"\nProcessing C file: {file_path}")
        print(f"Absolute path: {abs_path}")
        print(f"Base directory: {base_dir}")
        
        # Create a Document from the C code with file path information
        document = Document(
            text=c_code,
            metadata={
                "filepath": abs_path,
                "base_dir": base_dir
            }
        )
        
        # Configure the enhanced CodeSplitter
        code_splitter = CodeSplitter(
            language="c",
            chunk_lines=10,  # Adjust as needed
            chunk_lines_overlap=5,  # Adjust as needed
            max_chars=256,  # Adjust as needed
        )
        
        # Split the document into nodes with enhanced metadata
        nodes = code_splitter.get_nodes_from_documents([document])
        
        print(f"\nDocument split into {len(nodes)} nodes")
        
        # Print info about each node with enhanced metadata
        for i, node in enumerate(nodes):
            print(f"\nNode {i+1}:")
            print(f"- Text length: {len(node.text)}")
            
            # Print file path information
            print("- File information:")
            print(f"  • Filename: {node.metadata.get('filename', 'N/A')}")
            print(f"  • Filepath: {node.metadata.get('filepath', 'N/A')}")
            print(f"  • Relative path: {node.metadata.get('relpath', 'N/A')}")
            
            # Print line number information
            print("- Line information:")
            print(f"  • Start line: {node.metadata.get('start_line', 'N/A')}")
            print(f"  • End line: {node.metadata.get('end_line', 'N/A')}")
            
            # Print text preview
            preview = node.text[:50].replace('\n', '\\n')
            print(f"- Preview: {preview}...")
            
        # Create a simple index from the nodes
        index = VectorStoreIndex(nodes)
        
        # Demonstrate filtering by file and line information
        print("\nDemonstrating metadata filtering capabilities:")
        
        # Filter nodes by filename
        filename = os.path.basename(file_path)
        filename_filtered = [node for node in nodes if node.metadata.get("filename") == filename]
        print(f"- Found {len(filename_filtered)} nodes from file '{filename}'")
        
        # Filter nodes by line range (e.g., find nodes containing line 20)
        target_line = 20  # Can be adjusted based on the file
        line_filtered = [
            node for node in nodes 
            if node.metadata.get("start_line", 0) <= target_line and node.metadata.get("end_line", 0) >= target_line
        ]
        print(f"- Found {len(line_filtered)} nodes containing line {target_line}")
        
        return nodes, index
        
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def main():
    # Check if a file path was provided
    if len(sys.argv) < 2:
        print("Error: No file path provided.")
        print(f"Usage: python {sys.argv[0]} <path_to_c_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        # Setup tree-sitter C parser
        c_language, library_path = setup_tree_sitter()
        if c_language is None:
            print("Failed to set up tree-sitter. Exiting.")
            return
            
        # Process the C file with enhanced CodeSplitter
        print("\nProcessing C file with enhanced CodeSplitter...")
        nodes, index = process_c_file_with_enhanced_splitter(file_path)
        
        if nodes and index:
            print("\nSuccessfully processed C file with enhanced metadata!")
            
            # Print a summary of the results
            print("\nSummary:")
            print(f"- Total nodes: {len(nodes)}")
            print(f"- File processed: {os.path.basename(file_path)}")
            print(f"- Metadata fields: filename, filepath, relpath, start_line, end_line")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()