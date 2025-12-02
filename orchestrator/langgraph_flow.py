# orchestrator/langgraph_flow.py
from langgraph.graph import StateGraph # type: ignore
from typing import TypedDict, Optional
from agents import repo_analyzer, embedding_agent, metadata_recommender, content_improver, reviewer
from agents.embedding_agent import EmbeddingAgent
from tools.text_splitter import split_text

class PipelineState(TypedDict):
    repo_path: str
    repo_summary: Optional[dict]
    metadata: Optional[dict]
    improved: Optional[dict]
    review: Optional[dict]

def analyze_repo(state: PipelineState) -> PipelineState:
    summary = repo_analyzer.analyze_repo(state["repo_path"])
    return {"repo_summary": summary}

def embed_repo(state: PipelineState) -> PipelineState:
    summary = state["repo_summary"]
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
    return {}  # no change to state

def suggest_metadata(state: PipelineState) -> PipelineState:
    meta = metadata_recommender.suggest(state["repo_summary"])
    return {"metadata": meta}

def improve_content(state: PipelineState) -> PipelineState:
    improved = content_improver.improve(state["repo_summary"], state["metadata"])
    return {"improved": improved}

def review_content(state: PipelineState) -> PipelineState:
    rev = reviewer.review(state["repo_summary"], state["improved"])
    return {"review": rev}

# Build the graph
graph = StateGraph(PipelineState)

graph.add_node("analyze", analyze_repo)
graph.add_node("embed", embed_repo)
graph.add_node("metadata", suggest_metadata)
graph.add_node("improve", improve_content)
graph.add_node("review", review_content)

graph.set_entry_point("analyze")
graph.add_edge("analyze", "embed")
graph.add_edge("embed", "metadata")
graph.add_edge("metadata", "improve")
graph.add_edge("improve", "review")
graph.add_edge("review", "__end__")

app = graph.compile()

def run_langgraph_pipeline(repo_path: str):
    initial_state = {"repo_path": repo_path, "repo_summary": None, "metadata": None, "improved": None, "review": None}
    result = app.invoke(initial_state)
    return result

if __name__ == "__main__":
    import sys
    repo = sys.argv[1] if len(sys.argv) > 1 else "data/sample_repo"
    res = run_langgraph_pipeline(repo)
    print("Pipeline completed.")
    print("Metadata:", res.get("metadata"))
    print("Review:", res.get("review"))