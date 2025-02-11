# 6_rag_example.py

###################
# 1) Bag-of-Words Embedding
###################
VOCABULARY = ["the", "cat", "dog", "apple", "banana", "run", "walk", "blue", "sky", 
              "apples", "bananas", "sat", "mat", "jumped", "over", "delicious"]

def text_to_bow(text):
    tokens = text.lower().split()
    bow_vector = [0] * len(VOCABULARY)
    for word in tokens:
        if word in VOCABULARY:
            idx = VOCABULARY.index(word)
            bow_vector[idx] += 1
    return bow_vector

###################
# 2) Euclidean Distance
###################
def euclidean_distance(vec1, vec2):
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must be same length.")
    sum_of_squares = 0.0
    for i in range(len(vec1)):
        diff = vec1[i] - vec2[i]
        sum_of_squares += diff * diff
    return sum_of_squares ** 0.5

###################
# 3) Simple Vector Database
###################
class SimpleVectorDB:
    def __init__(self):
        self.data = []
    
    def add(self, text, embedding):
        self.data.append((text, embedding))
    
    def search(self, query_embedding, k=1):
        results = []
        for (text, emb) in self.data:
            dist = euclidean_distance(query_embedding, emb)
            print(text, " : ", dist)
            results.append((text, dist))
        results.sort(key=lambda x: x[1])
        return results[:k]

###################
# 4) Text Chunking
###################
def chunk_text(document, max_sentence_length=80):
    sentences = document.split('.')
    chunks = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            if len(sentence) > max_sentence_length:
                sentence = sentence[:max_sentence_length]
            chunks.append(sentence)
    return chunks

###################
# 5) Complete Workflow
###################
if __name__ == "__main__":
    # Our sample corpus
    document = (
        "The cat sat on the mat. "
        "Then the cat jumped over the dog. "
        "Apples and bananas are delicious. "
        "I love to walk under the blue sky."
    )
    
    # 1) Chunk the text
    chunks = chunk_text(document)
    
    # 2) Create a vector DB and insert chunks
    db = SimpleVectorDB()
    for chunk in chunks:
        emb = text_to_bow(chunk)
        db.add(chunk, emb)
    
    # 3) Suppose a user query
    query = "cat dog jumped"
    query_embedding = text_to_bow(query)
    
    # 4) Search for the most relevant chunk
    top_k = 1
    results = db.search(query_embedding, k=top_k)
    print(results)

    # 5) Display the retrieved chunk(s) and form a naive answer
    print("Query:", query)
    for i, (res_text, dist) in enumerate(results):
        print(f"Retrieved chunk #{i+1} (Distance={dist:.2f}): {res_text}")
    
    # (Optional) Construct an answer from retrieved chunk(s)
    # A real RAG system would feed the chunk + query to an LLM for generation.
    # For demonstration, we just print the chunk as "the answer."
    best_chunk, _ = results[0]
    answer = f"The text says: '{best_chunk}'."
    print("Answer:", answer)

