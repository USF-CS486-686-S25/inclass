from rich import print
from rich.pretty import Pretty

from llama_index.core import Settings
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import CodeSplitter

# Create a code splitter instance
code_splitter = CodeSplitter(
    language="c",  # Default language
    chunk_lines=40,    # Number of lines per chunk
    chunk_lines_overlap=15,  # Number of overlapping lines between chunks
    max_chars=1500,    # Maximum characters per chunk
)

# Load documents
reader = SimpleDirectoryReader(input_dir="xv6-riscv",
                             recursive=True)
documents = reader.load_data()

print(f"Loaded {len(documents)} documents")

# Process documents with CodeSplitter
nodes = code_splitter.get_nodes_from_documents(documents)
print(f"Created {len(nodes)} code chunks")

# Create index from the processed nodes
index = VectorStoreIndex(nodes)

query_engine = index.as_query_engine(response_mode="tree_summarize",
                                   verbose=True,)

#response = query_engine.query("What is the maximum number of processes supported in xv6?")

#response = query_engine.query("How is access to pipes synchronized?")

#response = query_engine.query("How do I add a new system call?")

response = query_engine.query("What files, functions, and lines of code are responsible for process creation?")

print("=== RESPONSE DETAILS ===")
print(response)

print("=== RESPONSE ===")
print(response.response)

print("=== LLM ===")
print(Settings.llm)