"""RAG smoke test: 4 questions (3 in-doc, 1 out-of-doc -> should refuse).

Run:
    python -m soc_copilot.demos.rag_demo
"""
from soc_copilot.rag import build_index, make_retriever, make_rag_chain

QUESTIONS = [
    "What is the power consumption of the SHA-256 accelerator?",  # not in doc -> refuse
    "How does the FIFO handle metastability?",
    "What is the read latency of the AXI4-Lite slave?",
    "What is the price of NVIDIA H100?",                          # out of scope -> refuse
]


def main():
    chunks, vs = build_index()
    retriever = make_retriever("semantic", vs, chunks, k=3)
    rag = make_rag_chain(retriever)
    print(f"Index built: {len(chunks)} chunks\n")

    for q in QUESTIONS:
        print("=" * 60)
        print(f"Q: {q}")
        print(f"A: {rag.invoke(q)}\n")


if __name__ == "__main__":
    main()
