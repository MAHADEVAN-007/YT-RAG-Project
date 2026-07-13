from pinecone import Pinecone, ServerlessSpec

from backend.config import settings


_pc = None


def get_pinecone():
    global _pc
    if _pc is None:
        _pc = Pinecone(api_key=settings.pinecone_api_key)
        _ensure_index(_pc)
    return _pc


def _ensure_index(pc: Pinecone):
    index_name = settings.pinecone_index_name
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=settings.pinecone_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return pc.Index(index_name)


def get_index():
    return get_pinecone().Index(settings.pinecone_index_name)


def upsert_vectors(
    vectors: list[tuple[str, list[float], dict]],
    namespace: str,
    batch_size: int = 100,
):
    index = get_index()
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        index.upsert(vectors=batch, namespace=namespace)


def query_vectors(
    vector: list[float],
    top_k: int = 5,
    namespace: str | None = None,
    filter: dict | None = None,
) -> list[dict]:
    index = get_index()
    result = index.query(
        vector=vector,
        top_k=top_k,
        namespace=namespace,
        filter=filter,
        include_metadata=True,
    )
    return result.get("matches", [])
