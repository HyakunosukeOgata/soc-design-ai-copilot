# Day 4 — Eval Pipeline (Retrieval + Faithfulness)

## 今天做了什麼
建了一條完整的 RAG 評估管線，用數字證明 retriever 與 generation 的品質。

### 產出
- `eval/golden.jsonl` — 16 題 golden set（15 retrieval + 1 refusal）
- `eval/run_retrieval.py` — Recall@1/3/5 + MRR for 4 retrievers
- `eval/run_faithfulness.py` — LLM-as-judge 評 faithfulness + refusal
- `eval/reports/retrieval_report.md`、`faithfulness_report.md`

---

## 兩層測試結果

### L1 Retrieval（chunk 對不對？）
| Retriever       | R@1  | R@3  | R@5  | MRR   |
|-----------------|------|------|------|-------|
| **Semantic**    | 0.73 | 1.00 | 1.00 | **0.867** |
| BM25            | 0.60 | 0.87 | 0.87 | 0.711 |
| Hybrid          | 0.67 | 0.87 | 1.00 | 0.800 |
| Hybrid+Rerank   | 0.47 | 0.87 | 1.00 | 0.678 |

→ **最簡單的贏**。原因：corpus 只有 11 chunks（BM25 starve）+ 通用 ms-marco reranker 不懂 SoC 領域。

### L2 Generation（答案有依據嗎？）
- **Faithfulness**: 13/15 = 86.67%
- **Refusal Acc**: 1/1 = 100%
- 2 題 FAIL 其實是模型正確拒答 spec 沒寫的功耗 → golden set 自己有問題

---

## 核心觀念

### 4 個指標
- **Recall@k** = 正確 chunk 是否出現在前 k 個
- **MRR** = 1/rank 平均，獎勵「排越前面越好」
- **Faithfulness** = 答案是否 grounded in context（LLM-as-judge）
- **Refusal Accuracy** = 該拒答時有沒有拒

### Substring match 不是 exact match
chunking 切完邊界不可預測，golden set 寫 "32 bits" 比 "address width is 32 bits" 更穩健。

### LLM-as-judge 的 prompt 關鍵
- temperature=0
- 強制 JSON 輸出（JsonOutputParser）
- 只問「有沒有 grounding」，不要問「答得好不好」（後者主觀）

---

## 面試 Soundbites

> 「我為 RAG 建了 16 題 golden set 分兩層評估：retrieval 用 Recall@k/MRR，generation 用 LLM-as-judge 測 faithfulness。」

> 「實驗結果反直覺 — 加了 reranker 反而 MRR 降 22%。我 debug 後發現是通用 ms-marco 不懂 SoC 領域 + BM25 在小 corpus 飢餓。這讓我學到不是越多元件越好，要 measure 才知道。」

> 「Faithfulness 86.67%，2 個 FAIL case 分析後發現是模型正確拒答 spec 沒寫的功耗 — eval 不只測 model，也在 audit 你的 test set。」

> 「Refusal accuracy 100% 對 production RAG 很重要 — 寧可說『我不知道』也不能 hallucinate。」

---

## Quiz 補強筆記（必背 3 關鍵字）

### 關鍵字 1：Reproducibility（為什麼 judge 要 temperature=0）
- Eval 必須 deterministic，不然你不知道分數變動是「prompt 改了」還是「judge 抖動」
- temperature=0.7 的 judge → 自己就 ±5% 抖動，會蓋過你想觀察的訊號
- 強制 JSON schema 也是同理：自由輸出會讓 parser fail = 假 FAIL
- **口訣**：Eval 要的是 determinism，不是 creativity

### 關鍵字 2：救通用 reranker 的 2 個具體手段
1. **Domain fine-tune**：用自己 corpus 生成 query-chunk pair + 人工標 relevance 微調 cross-encoder（~1k 對就有效）
2. **Threshold gating / Score blending**：reranker score 差距太小時保留原 hybrid 排序；或用 `final = 0.7*orig_rank + 0.3*rerank_score` 避免 reranker 完全主導
- ❌ 不要回答「換 model」這種廢話
- ✅ 關鍵字：fine-tune、domain adaptation、threshold gating、score blending

### 關鍵字 3：擴 eval set 的三階段路徑
- Phase 1（現在）：手寫 16 題 golden set，目的是 smoke test / sanity check
- Phase 2：LLM 自動 **synthesize** Q&A pairs（給 chunk 讓 GPT 出題），擴到 200+
- Phase 3：上線後收 **user query log** + 人工標註，做真實分布的 eval set
- **金句**：「16 題是冷啟動，目的先確認 pipeline 沒爛掉。Production 後 eval set 應由真實 user query 驅動，才有 statistical power。」

### Schema 升級：三態 answer_type
binary `should_refuse` 不夠用，會把「正確的謙虛」誤判成 FAIL。
```json
{
  "answer_type": "answerable" | "refusable" | "unanswerable"
  // answerable: 必須答對
  // refusable: 答對 OR 拒答都 PASS（spec 沒寫但合理拒答，例如 q01 功耗）
  // unanswerable: 必須拒答（例如 q16 H100 pricing）
}
```
**金句**：「我發現 eval pipeline 把模型『正確的謙虛』誤判成失敗 — 這暴露 binary schema 不夠用。Production 場景中『不知道』是合法答案，eval 要 model 它。」

### MRR vs Recall 補充金句
> 「Recall@k 是 binary（中沒中），MRR 是 graded（多前面中）。Production user 只看 top 1-2，所以 MRR 比 Recall@10 更貼近真實體驗。」

---

## Day 4 Done ✅
Days 1-4 全部上線。明天 Day 5 開 GitHub repo + 重構成 src/ 專案結構。
