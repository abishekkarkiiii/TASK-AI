def sentence_chunking(
    text: str,
    chunk_size: int = 500
) -> list[str]:

    sentences = text.split(".")
    chunks = []

    current_chunk = ""

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + ". "

        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def fixed_size_chunking(
    text: str,
    chunk_size: int = 500
) -> list[str]:

    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)

    return chunks