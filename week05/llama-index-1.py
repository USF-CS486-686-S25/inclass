from rich import print
from rich.pretty import Pretty

from llama_index.core import Document
from llama_index.core import VectorStoreIndex

# Prepare some example documents (synthetic data for demonstration)
text_list = [
    "Alice went to the market to buy apples and oranges.",
    "Bob loves to play the guitar on weekends with his band."
]
documents = [Document(text=t) for t in text_list]  # Wrap each text string as a Document

for d in documents:
    print(Pretty(d))
    
