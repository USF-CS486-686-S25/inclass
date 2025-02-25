from rich import print
from rich.pretty import Pretty

from llama_index.core import Settings
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.core import SimpleDirectoryReader

reader = SimpleDirectoryReader(input_dir="xv6-riscv",
                                  recursive=True)
documents = reader.load_data()

print(Pretty(documents[0]))
print(Pretty(documents[20]))

print(f"Loaded {len(documents)} documents")

index = VectorStoreIndex.from_documents(documents)

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
