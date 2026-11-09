"""
Inspection script to view the chunks and their vector embeddings stored in ChromaDB.
Prints document IDs, metadata, text chunks, and embedding vector details (dimension, sample values, norm).
"""

import math
from typing import Optional
import chromadb
from src.config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR


def inspect_chromadb_embeddings(limit: int = 5, show_full_vector: bool = False):
    """
    Connect to ChromaDB and display stored chunks along with their vector embeddings.
    """
    print(f"=== Connecting to ChromaDB ===")
    print(f"Path: {CHROMA_PERSIST_DIR}")
    print(f"Collection: {CHROMA_COLLECTION_NAME}\n")

    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_collection(CHROMA_COLLECTION_NAME)

    total_count = collection.count()
    print(f"Total Chunks in ChromaDB: {total_count}")
    print("=" * 80)

    # Fetch data including embeddings, documents, and metadatas
    records = collection.get(
        include=["embeddings", "documents", "metadatas"],
        limit=limit
    )

    ids = records.get("ids", [])
    documents = records.get("documents", [])
    metadatas = records.get("metadatas", [])
    embeddings = records.get("embeddings", [])

    for idx, (doc_id, doc_text, meta, emb) in enumerate(zip(ids, documents, metadatas, embeddings), 1):
        dim = len(emb) if emb is not None else 0
        
        # Calculate L2 norm (vector magnitude)
        l2_norm = math.sqrt(sum(x * x for x in emb)) if emb is not None else 0.0

        # Sample values for readability
        sample_preview = (
            [round(val, 4) for val in emb[:6]] + ["..."] + [round(val, 4) for val in emb[-3:]]
            if emb is not None and len(emb) > 9 else []
        )

        print(f"[{idx}] Chunk ID : {doc_id}")
        print(f"    Scheme   : {meta.get('scheme_name')}")
        print(f"    Field    : {meta.get('field_name')}")
        print(f"    Source   : {meta.get('source_url')}")
        print(f"    Text     : \"{doc_text}\"")
        print(f"    Vector Dimension : {dim} dimensions")
        print(f"    Vector L2 Norm   : {round(l2_norm, 4)} (Cosine normalized)")
        print(f"    Vector Sample    : {sample_preview}")

        if show_full_vector:
            print(f"    Full Vector      : {emb}")

        print("-" * 80)


if __name__ == "__main__":
    inspect_chromadb_embeddings(limit=5)

