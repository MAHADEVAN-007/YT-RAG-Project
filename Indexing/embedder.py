from sentence_transformers import SentenceTransformer

_model = None

model_name = "all-MiniLM-L6-v2"

def get_embedder(model_name: str = model_name):
    global _model
    if _model is None:
        _model = SentenceTransformer(model_name)
    return _model


def embed_chunks(chunks: list[dict], batch_size: int = 32, model_name: str = model_name):
    model = get_embedder(model_name)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=False)
    return [{"text": text, "embedding": embedding} for text, embedding in zip(texts, embeddings)]