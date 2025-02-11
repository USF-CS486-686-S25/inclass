# We'll define a simple global vocabulary for demonstration.
# In practice, you might build the vocabulary from your entire corpus or use a more advanced tokenizer.

VOCABULARY = ["the", "cat", "dog", "apple", "banana", "run", "walk", "blue", "sky"]


def text_to_bow(text):
    """
    Convert text to a simple Bag-of-Words vector based on the global VOCABULARY.
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

# Example usage:
if __name__ == "__main__":
    print()
    print("Vocabulary: ", VOCABULARY)
    print()

    text1 = "The cat and the dog run under a blue sky."
    text1_embedding = text_to_bow(text1)
    print("Text 1:     ", text1)
    print("Embedding:  ", text1_embedding)
    print()

    text2 = "The dog apple banana."
    text2_embedding = text_to_bow(text2)
    print("Text 2:     ", text2)
    print("Embedding:  ", text2_embedding)
    print()

    text3 = "The cat, dog, and blue banana."
    text3_embedding = text_to_bow(text3)
    print("Text 3:     ", text3)
    print("Embedding:  ", text3_embedding)
    print()

    print("Distance(text3,text1) = ", euclidean_distance(text3_embedding, text1_embedding
))
    print("Distance(text3,text2) = ", euclidean_distance(text3_embedding, text2_embedding
))

