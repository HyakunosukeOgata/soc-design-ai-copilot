"""
eval/run_retrieval.py — Recall@k + MRR for 4 retrievers.

Uses src.rag.ingest to load + chunk + build vectorstore.
Builds retrievers here (with K*2 pool trick for reranker).

Run:
    python -m eval.run_retrieval
"""
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import FlashrankRerank

from src.rag.ingest import load_documents, split_documents, build_vectorstore

# ---------- Load eval set ----------
GOLDEN = Path("eval/golden.jsonl")
golden = [json.loads(l) for l in GOLDEN.read_text(encoding="utf-8").splitlines() if l.strip()]
ret_golden = [g for g in golden if not g.get("should_refuse")]
print(f"Loaded {len(golden)} golden Qs ({len(ret_golden)} for retrieval eval)")

# ---------- Build retrievers ----------
chunks = split_documents(load_documents())
vs = build_vectorstore(chunks)
print(f"  {len(chunks)} chunks")

K = 5
semantic_r = vs.as_retriever(search_kwargs={"k": K})
bm25_r = BM25Retriever.from_documents(chunks); bm25_r.k = K
hybrid_r = EnsembleRetriever(retrievers=[semantic_r, bm25_r], weights=[0.5, 0.5])

# Reranker pool: 2*K so reranker has things to reorder
hybrid_pool = EnsembleRetriever(
    retrievers=[
        vs.as_retriever(search_kwargs={"k": K * 2}),
        BM25Retriever.from_documents(chunks),
    ],
    weights=[0.5, 0.5],
)
hybrid_pool.retrievers[1].k = K * 2
rerank_r = ContextualCompressionRetriever(
    base_compressor=FlashrankRerank(top_n=K),
    base_retriever=hybrid_pool,
)

retrievers = {
    "Semantic": semantic_r,
    "BM25": bm25_r,
    "Hybrid": hybrid_r,
    "Hybrid+Rerank": rerank_r,
}

# ---------- Eval ----------
def find_rank(retrieved_docs, expected_substr):
    for i, doc in enumerate(retrieved_docs, 1):
        if expected_substr in doc.page_content:
            return i
    return None

def evaluate(name, retriever):
    hits = {1: 0, 3: 0, 5: 0}
    rr_sum = 0.0
    misses = []
    for g in ret_golden:
        retrieved = retriever.invoke(g["question"])
        rank = find_rank(retrieved, g["expected_chunk_contains"])
        if rank is None:
            misses.append(g["id"])
            continue
        for k in (1, 3, 5):
            if rank <= k:
                hits[k] += 1
        rr_sum += 1.0 / rank
    n = len(ret_golden)
    return {"name": name, "r1": hits[1]/n, "r3": hits[3]/n, "r5": hits[5]/n,
            "mrr": rr_sum/n, "misses": misses}

print(f"\nEvaluating {len(retrievers)} retrievers on {len(ret_golden)} Qs (K={K})...")
results = [evaluate(name, r) for name, r in retrievers.items()]

print("\n" + "=" * 70)
print(f"{'Retriever':<18} | {'R@1':>6} | {'R@3':>6} | {'R@5':>6} | {'MRR':>6}")
print("-" * 70)
for r in results:
    print(f"{r['name']:<18} | {r['r1']:>6.2f} | {r['r3']:>6.2f} | {r['r5']:>6.2f} | {r['mrr']:>6.3f}")
print("=" * 70)

print(f"\n[Misses per retriever] (NOT in top-{K})")
for r in results:
    print(f"  {r['name']}: {r['misses'] or '(none)'}")

# ---------- Report ----------
report_path = Path("eval/reports/retrieval_report.md")
report_path.parent.mkdir(parents=True, exist_ok=True)
with report_path.open("w", encoding="utf-8") as f:
    f.write(f"# Retrieval Eval Report\n\nEval set: {len(ret_golden)} Qs, K={K}\n\n")
    f.write("| Retriever | R@1 | R@3 | R@5 | MRR |\n|---|---|---|---|---|\n")
    for r in results:
        f.write(f"| {r['name']} | {r['r1']:.2f} | {r['r3']:.2f} | {r['r5']:.2f} | {r['mrr']:.3f} |\n")
    f.write("\n## Misses\n\n")
    for r in results:
        f.write(f"- **{r['name']}**: {r['misses'] or 'none'}\n")
print(f"\nReport saved to {report_path}")
