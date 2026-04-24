"""Retrieval eval: Recall@1/3/5 + MRR for all retriever variants.

Run:
    python -m soc_copilot.eval.run_retrieval
"""
import json
from soc_copilot.config import GOLDEN_PATH, REPORTS_DIR
from soc_copilot.rag import build_index, make_retriever

K = 5
RETRIEVER_KINDS = ["semantic", "bm25", "hybrid", "hybrid_rerank"]
NAME = {
    "semantic": "Semantic",
    "bm25": "BM25",
    "hybrid": "Hybrid",
    "hybrid_rerank": "Hybrid+Rerank",
}


def find_rank(retrieved_docs, expected_substr: str) -> int | None:
    """Position (1-based) of first chunk containing the substring, else None."""
    for i, doc in enumerate(retrieved_docs, 1):
        if expected_substr in doc.page_content:
            return i
    return None


def evaluate(name, retriever, golden):
    hits = {1: 0, 3: 0, 5: 0}
    rr_sum = 0.0
    misses = []
    for g in golden:
        rank = find_rank(retriever.invoke(g["question"]), g["expected_chunk_contains"])
        if rank is None:
            misses.append(g["id"])
            continue
        for k in (1, 3, 5):
            if rank <= k:
                hits[k] += 1
        rr_sum += 1.0 / rank
    n = len(golden)
    return {
        "name": name,
        "r1": hits[1] / n, "r3": hits[3] / n, "r5": hits[5] / n,
        "mrr": rr_sum / n, "misses": misses,
    }


def main():
    golden = [json.loads(l) for l in GOLDEN_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    ret_golden = [g for g in golden if not g.get("should_refuse")]
    print(f"Loaded {len(golden)} golden Qs ({len(ret_golden)} for retrieval eval)")

    chunks, vs = build_index()
    print(f"  {len(chunks)} chunks")

    results = []
    for kind in RETRIEVER_KINDS:
        retriever = make_retriever(kind, vs, chunks, k=K)
        results.append(evaluate(NAME[kind], retriever, ret_golden))

    # Print
    print("\n" + "=" * 70)
    print(f"{'Retriever':<18} | {'R@1':>6} | {'R@3':>6} | {'R@5':>6} | {'MRR':>6}")
    print("-" * 70)
    for r in results:
        print(f"{r['name']:<18} | {r['r1']:>6.2f} | {r['r3']:>6.2f} | {r['r5']:>6.2f} | {r['mrr']:>6.3f}")
    print("=" * 70)

    print(f"\n[Misses] (NOT in top-{K})")
    for r in results:
        print(f"  {r['name']}: {r['misses'] or '(none)'}")

    # Report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = REPORTS_DIR / "retrieval_report.md"
    with report.open("w", encoding="utf-8") as f:
        f.write(f"# Retrieval Eval Report\n\nEval set: {len(ret_golden)} Qs, K={K}\n\n")
        f.write("| Retriever | R@1 | R@3 | R@5 | MRR |\n|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r['name']} | {r['r1']:.2f} | {r['r3']:.2f} | {r['r5']:.2f} | {r['mrr']:.3f} |\n")
        f.write("\n## Misses\n\n")
        for r in results:
            f.write(f"- **{r['name']}**: {r['misses'] or 'none'}\n")
    print(f"\nReport saved to {report.relative_to(REPORTS_DIR.parent.parent)}")


if __name__ == "__main__":
    main()
