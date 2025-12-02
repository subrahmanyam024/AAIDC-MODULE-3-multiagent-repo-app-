# orchestrator/simple_pipeline.py
import asyncio
from agents import repo_analyzer, embedding_agent, metadata_recommender, content_improver, reviewer
from agents.embedding_agent import EmbeddingAgent
from tools.text_splitter import split_text

async def run_pipeline(repo_path):
    # 1. analyze.
    summary = repo_analyzer.analyze_repo(repo_path)
    # 2. split & embed all files (code + docs)
    emb = EmbeddingAgent()
    chunks = []
    metas = []
    for f in summary["files"]:
        parts = split_text(f["content"])
        for p in parts:
            chunks.append(p)
            metas.append({"source": f["path"]})
    print(f"Embedding {len(chunks)} chunks ...")
    emb.add_texts(chunks, metadata_list=metas)
    # 3. metadata suggestions
    meta = metadata_recommender.suggest(summary)
    # 4. content improv
    improved = content_improver.improve(summary, meta)
    # 5. review
    rev = reviewer.review(summary, improved.get("improved_readme",""))
    return {"summary": summary, "metadata": meta, "improved": improved, "review": rev}

if __name__ == "__main__":
    import sys, json
    repo = sys.argv[1] if len(sys.argv) > 1 else "data/sample_repo"
    res = asyncio.run(run_pipeline(repo))
    print(json.dumps({"metadata": res["metadata"], "review": res["review"]}, indent=2))
