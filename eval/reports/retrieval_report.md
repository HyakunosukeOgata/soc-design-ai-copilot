# Retrieval Eval Report

Eval set: 15 Qs, K=5

| Retriever | R@1 | R@3 | R@5 | MRR |
|---|---|---|---|---|
| Semantic | 0.73 | 1.00 | 1.00 | 0.867 |
| BM25 | 0.60 | 0.87 | 0.87 | 0.711 |
| Hybrid | 0.67 | 0.87 | 1.00 | 0.800 |
| Hybrid+Rerank | 0.67 | 0.80 | 1.00 | 0.772 |

## Misses

- **Semantic**: none
- **BM25**: ['q08', 'q15']
- **Hybrid**: none
- **Hybrid+Rerank**: none
