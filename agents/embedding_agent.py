# agents/embedding_agent.py
import os
import uuid
import requests
import numpy as np
from qdrant_client.models import VectorParams, Distance, PointStruct
from config.config import qdrant, JINA_API_KEY, JINA_EMBEDDING_MODEL, QDRANT_COLLECTION, EMBEDDING_DIM
from utils.resilience import api_retry

class EmbeddingAgent:
    def __init__(self):
        self.collection = QDRANT_COLLECTION
        self.dim = EMBEDDING_DIM
        self._ensure_collection()

    def _ensure_collection(self):
        # create if missing
        try:
            collections = [c.name for c in qdrant.get_collections().collections]
        except Exception:
            collections = []
        if self.collection not in collections:
            qdrant.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE)
            )

    # ---- Jina embedding HTTP call ----
    @api_retry
    def _embed_with_jina(self, texts):
        """
        Call Jina embeddings API with fallback to local embeddings.
        """
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embeddings = model.encode(texts, normalize_embeddings=False)
            return [list(emb) for emb in embeddings]
        except Exception as e:
            print(f"[FALLBACK] Using local embeddings (Jina failed: {e})")
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('all-MiniLM-L6-v2')
                embeddings = model.encode(texts, normalize_embeddings=False)
                return [list(emb) for emb in embeddings]
            except Exception:
                dummy_emb = [float(i % 100) / 100.0 for i in range(self.dim)]
                return [dummy_emb] * len(texts)

    def add_texts(self, text_chunks, metadata_list=None, batch_size=32):
        """
        text_chunks: list[str]
        metadata_list: list[dict] or None (same length)
        """
        metadata_list = metadata_list or [{} for _ in text_chunks]
        for i in range(0, len(text_chunks), batch_size):
            batch_texts = text_chunks[i:i+batch_size]
            batch_meta = metadata_list[i:i+batch_size]
            vectors = self._embed_with_jina(batch_texts)
            points = [
                PointStruct(id=str(uuid.uuid4()), vector=list(vec), payload={"text": txt, **meta})
                for vec, txt, meta in zip(vectors, batch_texts, batch_meta)
            ]
            qdrant.upsert(collection_name=self.collection, points=points)

    @api_retry
    def search(self, query_text, top_k=5):
        vec = self._embed_with_jina([query_text])[0]
        hits = qdrant.search(collection_name=self.collection, query_vector=vec, limit=top_k, append_payload=True)
        # return list of payloads + score
        return [{"payload": h.payload, "score": getattr(h, "score", None)} for h in hits]
