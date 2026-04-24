# SoC Design AI Copilot

> **RAG + Agent assistant for SoC / RTL designers.** Built to demonstrate production-quality LangChain pipelines with end-to-end evaluation.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Why this exists
Most RAG demos answer "what is RAG" from a 5-page blog post. Real SoC engineers ask:
- *"What's the read latency of this AXI4-Lite slave?"*
- *"Which keyword should I use for sequential logic?"*
- *"Is this clock domain crossing safe?"*

This repo answers those — and **measures** how well it does so.

## Features
- **Hybrid retrieval**: Semantic (Chroma) + BM25 + FlashRank reranker, all wired through LangChain's `EnsembleRetriever`
- **Evaluation pipeline**: Recall@k, MRR, LLM-as-judge faithfulness, refusal accuracy — with reproducible reports
- **Honest results**: simplest semantic retriever beat hybrid+rerank on a small SoC corpus (MRR 0.867 vs 0.678). Documented [here](eval/reports/retrieval_report.md).
- **Refusal-first**: 100% refusal accuracy on out-of-scope questions. Production RAG must say *"I don't know"* before it hallucinates.

## Quick start

```bash
git clone https://github.com/<you>/soc-design-ai-copilot.git
cd soc-design-ai-copilot

python -m venv .venv
.venv\Scripts\activate                  # Windows
# source .venv/bin/activate             # Linux/Mac

pip install -e .[dev]
cp .env.example .env                    # add your OPENAI_API_KEY

# Run a smoke test
python -m soc_copilot.demos.rag_demo

# Run evals
python -m soc_copilot.eval.run_retrieval
python -m soc_copilot.eval.run_faithfulness
```

## Project structure
```
src/soc_copilot/
├── rag/
│   ├── ingest.py       # Load + split + embed -> Chroma
│   ├── retriever.py    # Semantic / BM25 / Hybrid / Hybrid+Rerank factory
│   └── chain.py        # LCEL chain: question -> retriever -> LLM -> parser
├── eval/
│   ├── run_retrieval.py    # Recall@k + MRR
│   └── run_faithfulness.py # LLM-as-judge faithfulness + refusal
└── demos/
    ├── rag_demo.py
    └── hybrid_demo.py
data/sample_spec.md     # Sample SoC spec (AXI4-Lite, SHA-256, CDC FIFO)
eval/golden.jsonl       # 16 golden Q&A
eval/reports/           # Generated eval reports
```

## Evaluation results

### Retrieval (15 questions)
| Retriever       | R@1  | R@3  | R@5  | MRR   |
|-----------------|------|------|------|-------|
| **Semantic**    | 0.73 | 1.00 | 1.00 | **0.867** |
| BM25            | 0.60 | 0.87 | 0.87 | 0.711 |
| Hybrid          | 0.67 | 0.87 | 1.00 | 0.800 |
| Hybrid+Rerank   | 0.47 | 0.87 | 1.00 | 0.678 |

> **Counter-intuitive finding**: adding a generic reranker hurt MRR by 22%. Root cause: corpus is small (BM25 starves) and the off-the-shelf `ms-marco-MultiBERT` reranker has no SoC domain knowledge. **Lesson: measure before adding complexity.**

### Generation (15 + 1)
- Faithfulness: **86.67%** (no hallucinations detected)
- Refusal accuracy: **100%** (correctly refuses out-of-scope questions)

## Roadmap
- [ ] Wrap as FastAPI service (`/ask`, `/eval`)
- [ ] Add agent layer with RTL lint tool
- [ ] Domain fine-tune a reranker on synthetic Q&A pairs
- [ ] Expand golden set via LLM-synthesized Q&A + user query logs

## License
MIT
