# SoC Design AI Copilot

A RAG + Agent assistant for SoC / RTL design documentation, built with LangChain v1.
Comes with a quantitative eval pipeline (Recall@k, MRR, faithfulness, refusal accuracy).

## Why this project
SoC designers spend hours digging through specs, style guides, and tribal knowledge.
This repo demos a production-shape pipeline that retrieves answers from real docs and
evaluates itself with measurable signals — not vibes.

## Architecture

```
data/                    sample SoC spec (md/pdf supported)
    └─ sample_spec.md

src/rag/
  config.py              env vars, defaults
  ingest.py              load -> split -> embed -> Chroma
  retriever.py           4 strategies: semantic / bm25 / hybrid / hybrid+rerank
  chain.py               grounded answer chain (refuses when out of scope)

eval/
  golden.jsonl           16 hand-written Q&A (15 retrieval + 1 refusal)
  run_retrieval.py       Recall@1/3/5 + MRR per retriever
  run_faithfulness.py    LLM-as-judge faithfulness + refusal accuracy
  reports/               generated markdown reports

demos/                   early hello_* scripts kept for reference
```

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # PowerShell
pip install -e .

# .env  (required)
# OPENAI_API_KEY=sk-...

# inspect ingestion
python -m src.rag.ingest

# answer a few SoC questions end-to-end
python -m src.rag.chain

# run evals
python -m eval.run_retrieval
python -m eval.run_faithfulness
```

## Current numbers (sample_spec corpus, 11 chunks, 15+1 golden Qs)

### Retrieval
| Retriever       | R@1  | R@3  | R@5  | MRR   |
|-----------------|------|------|------|-------|
| **Semantic**    | 0.73 | 1.00 | 1.00 | **0.867** |
| BM25            | 0.60 | 0.87 | 0.87 | 0.711 |
| Hybrid          | 0.67 | 0.87 | 1.00 | 0.800 |
| Hybrid+Rerank   | 0.47 | 0.87 | 1.00 | 0.678 |

### Generation
- Faithfulness: **13/15 = 86.67%**
- Refusal accuracy: **1/1 = 100%**

### What the numbers tell us
- Simplest retriever wins on this small corpus — BM25 starves on 11 chunks, generic
  ms-marco reranker does not understand SoC domain terms.
- 0 hallucinations: every answered question is grounded in the retrieved context.
- The 2 "FAIL" faithfulness cases are actually correct refusals on info the spec
  never contained — surfaces a binary-schema bug in the eval set itself.

## Roadmap
- [x] Day 1-3: LangChain LCEL + RAG + hybrid + reranker
- [x] Day 4: eval pipeline (retrieval + faithfulness)
- [x] Day 5: refactor into proper Python package
- [ ] Day 6: bigger corpus (OpenTitan / Ibex docs) + per-source attribution
- [ ] Day 7: FastAPI service + streaming
- [ ] Week 2: agent with RTL-lint tools + observability (LangSmith)

## License
MIT
