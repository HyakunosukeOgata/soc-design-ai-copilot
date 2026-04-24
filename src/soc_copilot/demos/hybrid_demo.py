"""Hybrid retrieval demo: side-by-side comparison of 4 retrievers.

Run:
    python -m soc_copilot.demos.hybrid_demo
"""
from soc_copilot.rag import build_index, make_retriever

QUERIES = [
    "How to handle clock crossing safely?",        # conceptual -> semantic should win
    "always_ff",                                    # rare keyword -> BM25 should win
    "energy usage of the hash module",              # synonym of "power consumption"
]
KINDS = ["semantic", "bm25", "hybrid", "hybrid_rerank"]


def show(name, docs):
    print(f"\n  [{name}] top-{len(docs)}")
    for i, d in enumerate(docs, 1):
        preview = d.page_content.replace("\n", " ")[:90]
        print(f"    {i}. {preview}...")


def main():
    chunks, vs = build_index()
    print(f"{len(chunks)} chunks\n")
    retrievers = {kind: make_retriever(kind, vs, chunks, k=3) for kind in KINDS}

    for q in QUERIES:
        print("\n" + "=" * 70)
        print(f"QUERY: {q}")
        print("=" * 70)
        for kind, r in retrievers.items():
            show(kind, r.invoke(q))


if __name__ == "__main__":
    main()
