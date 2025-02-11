VOCABULARY = ["the", "cat", "dog", "apple", "banana", "run", "walk", "blue", "sky"]


def text_to_bow(text):
    """
    Convert text to a simple Bag-of-Words vector based on the glo
bal VOCABULARY.
    text: string
    returns: list of integers, length == len(VOCABULARY)
    """
    # Convert text to lowercase and split by whitespace for simplicity
    tokens = text.lower().split()

    # Initialize vector with zeros, one for each vocabulary word
    bow_vector = [0] * len(VOCABULARY)

    for word in tokens:
        if word in VOCABULARY:
            idx = VOCABULARY.index(word)
            bow_vector[idx] += 1

    return bow_vector

def euclidean_distance(vec1, vec2):
    """
    Compute the Euclidean distance between two vectors.
    vec1, vec2: lists of numbers of the same length
    returns: float
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must be the same length.")

    sum_of_squares = 0.0
    for i in range(len(vec1)):
        diff = vec1[i] - vec2[i]
        sum_of_squares += diff * diff

    return sum_of_squares ** 0.5

class SimpleVectorDB:
    def __init__(self):
        # We will store a list of (text, embedding) pairs
        self.data = []

    def add(self, text, embedding):
        """
        Add a new text and its embedding to the database.
        """
        self.data.append((text, embedding))

    def search(self, query_embedding, k=1):
        """
        Find the top k nearest texts (smallest Euclidean distance) to the query_embedding
.
        Returns a list of (text, distance) sorted by distance ascending.
        """
        # We'll use the euclidean_distance function from earlier
        results = []
        for (text, emb) in self.data:
            dist = euclidean_distance(query_embedding, emb)
            results.append((text, dist))

        # Sort by distance
        results.sort(key=lambda x: x[1])

        # Return top k
        return results[:k]


# Example usage:
if __name__ == "__main__":
    # Initialize
    db = SimpleVectorDB()

    # Add some dummy entries
    #db.add("The cat ate an apple", [1, 1, 0, 1])  # example embedding
    #db.add("A dog likes bananas",  [0, 0, 1, 2])  # example embedding

    # Suppose our query has embedding [1, 0, 1, 0]
    #nearest = db.search([1, 0, 1, 0], k=1)
    #print("Nearest chunk:", nearest)

    text1 = "The cat and the dog run under a blue sky."
    db.add(text1, text_to_bow(text1))

    text2 = "The dog apple banana."
    db.add(text2, text_to_bow(text2))

    text3 = "The cat, dog, and blue banana."
    text3_embedding = text_to_bow(text3)

    nearest = db.search(text3_embedding, k=1)
    print("Nearest chunk:", nearest)
