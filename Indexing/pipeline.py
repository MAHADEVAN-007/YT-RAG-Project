import time
import logging
from typing import Any

from Indexing.chunker import chunk_transcript
from Indexing.embedder import embed_chunks
from Databases.Vector.pinecone_client import upsert_vectors

logger = logging.getLogger("yt_rag.indexing")


def index_transcript(
    video_id: str,
    transcript_text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
    batch_size: int = 32,
    log_extra: dict | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()
    log = dict(log_extra or {})

    t0 = time.perf_counter()
    chunks = chunk_transcript(transcript_text, chunk_size, chunk_overlap)
    t1 = time.perf_counter()
    chunk_latency = round((t1 - t0) * 1000, 2)
    logger.info("Chunking complete", extra={**log, "chunks": len(chunks), "latency_ms": chunk_latency})

    chunks = embed_chunks(chunks, batch_size=batch_size)
    t2 = time.perf_counter()
    embed_latency = round((t2 - t1) * 1000, 2)
    logger.info("Embedding complete", extra={**log, "chunks": len(chunks), "latency_ms": embed_latency})

    vectors = []
    for chunk in chunks:
        vector_id = f"{video_id}_{chunk['index']}"
        vectors.append((
            vector_id,
            chunk["embedding"],
            {
                "video_id": video_id,
                "chunk_index": chunk["index"],
                "text": chunk["text"],
            },
        ))

    upsert_vectors(vectors, namespace=video_id, batch_size=100)
    t3 = time.perf_counter()
    pinecone_latency = round((t3 - t2) * 1000, 2)
    logger.info("Pinecone upsert complete", extra={**log, "vectors": len(vectors), "latency_ms": pinecone_latency})

    total_latency = round((t3 - start) * 1000, 2)
    logger.info("Indexing pipeline finished", extra={**log, "total_latency_ms": total_latency})

    return {
        "video_id": video_id,
        "chunks": len(chunks),
        "total_latency_ms": total_latency,
    }
