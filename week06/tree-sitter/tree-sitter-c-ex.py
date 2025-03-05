from tree_sitter import Parser
from tree_sitter_languages import get_language, get_parser

# Get the C language parser
parser = get_parser('c')

# Sample C code with comments
c_code = """
/**
 * A simple program to demonstrate py-tree-splitter
 * with comments analysis
 */

#include <stdio.h>

// Function to calculate factorial
int factorial(int n) {
    // Base case
    if (n <= 1) {
        return 1; // Return 1 for n <= 1
    }
    
    /* Recursive case:
       multiply n by factorial of (n-1) */
    return n * factorial(n - 1);
}

int main() {
    int num = 5;
    // Calculate factorial
    int result = factorial(num);
    printf("Factorial of %d is %d\\n", num, result);
    return 0; // Exit successfully
}
"""

def simple_test():
    # Parse the code to get the AST
    tree = parser.parse(bytes(c_code, 'utf8'))

    # Get the root node of the AST
    root_node = tree.root_node

    # Print basic information about the AST
    print(f"AST type: {root_node.type}")
    print(f"AST children count: {len(root_node.children)}")
    print(f"AST text: {root_node.text.decode('utf8')[:50]}...")


def print_node_hierarchy(node, indent=0):
    """Print the node hierarchy with indentation to show the tree structure."""
    # Print the current node
    node_text = node.text.decode('utf8')
    # Truncate long text for display
    if len(node_text) > 30:
        node_text = node_text[:27] + '...'
    print(f"{'  ' * indent}{node.type}: '{node_text}'")
    
    # Print all children recursively
    for child in node.children:
        print_node_hierarchy(child, indent + 1)

# Parse the code to get the AST
tree = parser.parse(bytes(c_code, 'utf8'))

# Get the root node of the AST
root_node = tree.root_node


# Print the top-level nodes in the AST
for i, child in enumerate(root_node.children):
    print(f"Top-level node {i+1}:")
    print_node_hierarchy(child)
