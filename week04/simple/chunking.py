def chunk_text(document, max_sentence_length=80):
    """
    Very naive approach: split the document by periods,
    and treat each sentence as a chunk.
    max_sentence_length: optional limit on the number of characters for a chunk
    """
    sentences = document.split('.')
    chunks = []

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 0:
            # Optionally ensure we don't exceed max length
            if len(sentence) > max_sentence_length:
                # We could further split it if needed, but for simplicity,
                # let's just truncate or keep it as is.
                sentence = sentence[:max_sentence_length]
            chunks.append(sentence)

    return chunks


# Example usage:
if __name__ == "__main__":
    long_document = (
        "The cat sat on the mat. "
        "Then the cat jumped over the dog. "
        "Apples and bananas are delicious."
    )
    my_chunks = chunk_text(long_document)
    for i, chunk in enumerate(my_chunks):
        print(f"Chunk {i+1}: {chunk}")
