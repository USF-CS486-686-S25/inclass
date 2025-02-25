#!/usr/bin/env python3
"""
Using tree-sitter to parse C code in Python.
This program demonstrates how to:
1. Install and set up tree-sitter
2. Parse C code into a syntax tree
3. Navigate and query the syntax tree
"""

import os
from pathlib import Path
import sys

# You'll need to install these packages:
# pip install tree-sitter
try:
    from tree_sitter import Language, Parser
except ImportError:
    print("Error: tree-sitter package not found.")
    print("Please install it using: pip install tree-sitter")
    sys.exit(1)


def setup_tree_sitter():
    """
    Set up tree-sitter for C language parsing.
    This downloads and builds the C grammar if needed.
    """
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
        print("Setup complete!")
    
    # Load the C language
    C_LANGUAGE = Language(str(library_path), 'c')
    return C_LANGUAGE


def parse_c_code(code, language):
    """
    Parse C code using tree-sitter.
    Returns the root node of the syntax tree.
    """
    parser = Parser()
    parser.set_language(language)
    tree = parser.parse(bytes(code, 'utf8'))
    return tree.root_node


def print_node(node, code, level=0):
    """
    Print a node and its children recursively.
    """
    # Get the code text for this node
    code_text = code[node.start_byte:node.end_byte].decode('utf8')
    # Truncate long texts
    if len(code_text) > 50:
        code_text = code_text[:47] + "..."
    # Replace newlines and tabs for cleaner output
    code_text = code_text.replace('\n', '\\n').replace('\t', '\\t')
    
    indent = "  " * level
    print(f"{indent}{node.type}: '{code_text}'")
    
    # Print all child nodes
    for child in node.children:
        print_node(child, code, level + 1)


def query_functions(node, code, language):
    """
    Find and print all function definitions in the code.
    
    Args:
        node: The root node of the syntax tree
        code: The original code as bytes
        language: The tree-sitter Language object
    """
    query_string = "(function_definition) @function"
    
    query = language.query(query_string)
    captures = query.captures(node)
    
    print("\nFunctions found:")
    for i, (matched_node, _) in enumerate(captures):
        function_name = "unknown"
        
        # Try to find the function name in the declarator
        for child in matched_node.children:
            if child.type == "function_declarator":
                for declarator_child in child.children:
                    if declarator_child.type == "identifier":
                        function_name = code[declarator_child.start_byte:declarator_child.end_byte].decode('utf8')
        
        print(f"{i+1}. {function_name}")
        
        # Get function signature (first line)
        lines = code[matched_node.start_byte:matched_node.end_byte].decode('utf8').splitlines()
        if lines:
            print(f"   Signature: {lines[0]}")
        
        # Print location info
        print(f"   Line: {matched_node.start_point[0] + 1}, Column: {matched_node.start_point[1] + 1}")
        print()


def main():
    # Example C code to parse
    c_code = """
    #include <stdio.h>
    
    // A simple function to add two numbers
    int add(int a, int b) {
        return a + b;
    }
    
    // A function to calculate factorial
    int factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }
    
    int main() {
        int x = 5, y = 3;
        printf("Sum: %d\\n", add(x, y));
        printf("Factorial of %d: %d\\n", x, factorial(x));
        return 0;
    }
    """
    
    try:
        # Set up tree-sitter
        c_language = setup_tree_sitter()
        
        # Parse the code
        root_node = parse_c_code(c_code, c_language)
        
        # Print basic information about the parse tree
        print(f"Syntax tree root: {root_node.type}")
        print(f"Number of child nodes: {len(root_node.children)}")
        print(f"Text spans from byte {root_node.start_byte} to {root_node.end_byte}")
        
        # Ask if the user wants to see the full tree (it can be large)
        response = input("\nWould you like to see the full syntax tree? (y/n): ")
        if response.lower() == 'y':
            print("\nFull syntax tree:")
            print_node(root_node, bytes(c_code, 'utf8'))
        
        # Query the tree for functions
        query_functions(root_node, bytes(c_code, 'utf8'), c_language)
        
        # Demonstrate how to navigate to specific nodes
        print("Navigating to specific nodes:")
        if root_node.children:
            print(f"First top-level node type: {root_node.children[0].type}")
            
            # Find the main function
            for node in root_node.children:
                if node.type == "function_definition":
                    for child in node.children:
                        if child.type == "function_declarator":
                            for declarator_child in child.children:
                                if (declarator_child.type == "identifier" and 
                                    c_code[declarator_child.start_byte:declarator_child.end_byte] == "main"):
                                    print("Found main function!")
    
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Git is installed and you have permission to clone repositories.")


if __name__ == "__main__":
    main()
