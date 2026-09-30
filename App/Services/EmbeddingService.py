from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-mpnet-base-v2")

def create_embeddings(chunks: list[str]):
    return model.encode(chunks)