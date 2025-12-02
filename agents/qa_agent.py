# agents/qa_agent.py
from config.config import co
from agents.embedding_agent import EmbeddingAgent

class QAAgent:
    def __init__(self):
        self.emb = EmbeddingAgent()

    def answer(self, query, top_k=5):
        hits = self.emb.search(query, top_k=top_k)
        context = "\n\n".join([h["payload"].get("text","") for h in hits])
        prompt = f"Using the context below, answer the question concisely.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        
        resp = co.chat(
            message=prompt,
            model="command-a-03-2025",
            max_tokens=300
        )
        return resp.text.strip()
