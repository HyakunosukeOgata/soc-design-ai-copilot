# Week 1 Quiz Review — 答錯/不會的題目補強

> 12 題抽考結果整理。重點補強這 7 題。

---

## Q2. invoke / stream / batch 差別 ❌→補

- **`invoke(input)`**：同步，等全部跑完才回。最常用。
- **`stream(input)`**：邊產邊吐，generator → chatbot 打字機效果。
- **`batch([in1, in2, ...])`**：多 input 並行 → eval / 批次處理用。
- **`ainvoke / astream / abatch`** = async 版，給 FastAPI 高並發用。

| 場景 | 用 |
|---|---|
| 單次問答、寫腳本 | `invoke` |
| Chatbot UI | `stream` |
| 跑 eval set 100 題 | `batch` |
| FastAPI endpoint | `ainvoke` / `astream` |

**金句**：「invoke 求快寫；stream 求 UX；batch 求吞吐；async 求並發。」

---

## Q4. RAG 5 步驟 ⚠️→修正順序

正確分 2 個 phase：

**Phase 1 — Ingest（離線，建一次）**
1. **Load** — 讀文件
2. **Split** — 切 chunks
3. **Embed** — 轉向量
4. **Store** — 存進 Vector Store

**Phase 2 — Query（線上，每次問答）**
5. **Retrieve** — query embedding → vector search → top-k chunks → 餵給 LLM

**口訣：Load → Split → Embed → Store → Retrieve（LSESR）**

> Reranking 是選配；LLM answer 屬於 generation 不算 RAG 步驟。

---

## Q6. Embedding vs Vector Store ⚠️→細節修正

- **Embedding model**：文字 → 高維向量（如 1536 維）。query 跟 chunk 都要 embed。
- **Vector Store**：存所有 chunk 向量 + 提供「給 query 向量回傳 top-k 相似」的搜尋（內部用 ANN 索引：HNSW / IVF）

> Embedding ≠ indexing。Embedding 是「轉換」動作，indexing 是 vector store 內部建索引。

**沒 vector store 行不行？**
- 嚴格說可以（brute force 算 cosine，O(N)）
- 實務上不行（10M chunks 跑不動）

**金句**：「Vector store 不只是儲存 — 它是『相似度搜尋的 index』。沒它你就是 brute force。」

---

## Q7. Semantic vs BM25 ❌→例子講反了

**正確分工：**
| | BM25 | Semantic |
|---|---|---|
| 強項 | 罕見字 / 專有名詞 / 縮寫 | 同義詞 / paraphrase / 跨語言 |
| 機制 | 字面 token 比對（不懂同義）| Embedding 向量相似度 |
| 範例贏 | "always_ff"、"PCIe Gen5"、"AXI4-Lite" | "如何避免亞穩態" → match "metastability" |

**口訣**：BM25 抓**字**，Semantic 抓**意**。

**金句**：「BM25 強在 rare token，semantic 強在同義改寫。Hybrid 就是要兩邊互補 — 但實驗證明 corpus 太小時 BM25 反而拖後腿。」

---

## Q8. RRF（Reciprocal Rank Fusion）❌→補

公式：
$$\text{score}(d) = \sum_{i \in \text{retrievers}} \frac{1}{k + \text{rank}_i(d)}$$

白話：每個 retriever 給 doc d 一個排名，把 `1/(k+rank)` 加起來當總分。`k` 通常 60。

**為什麼這樣設計？**
- **Rank-based 不是 score-based** → 不需要兩邊 score 同尺度（semantic 0~1 vs BM25 幾百）
- 排名靠前權重大（rank=1 → 1/61），但靠後仍有貢獻

**金句**：「RRF 是 rank-based fusion — 解決多 retriever 分數量綱不同的問題。」

---

## Q9. 為什麼 Hybrid+Rerank 輸給 Semantic ❌→必背故事

**3 個根本原因：**
1. **Corpus 太小（11 chunks），BM25 飢餓** → 信號太弱反拖後腿
2. **通用 ms-marco reranker 沒有 SoC 領域知識** → 看到 `always_ff`、`AXI4-Lite` 會誤判
3. **Reranker 是 reorder 不是 retrieve** → hybrid 池子漏掉的正確 chunk，reranker 救不回來

**金句**：「Reranker 是 reorder 不是 retrieve — 池子裡沒有的東西，reranker 變不出來。」

> ⚠️ **這是 Week 1 最重要的故事，也是 README 第一個亮點。必須背熟因果鏈：
> 加 reranker → MRR 降 22% → root cause = 小 corpus + 通用 model + reranker 只能 reorder**

---

## Q12. 換 model 要改幾個地方 ❌→補

**理想答案：1 個地方**（`config.py` 的 `LLM_MODEL`）

**誠實答案：2 步**
1. 改 `config.py` 的 `LLM_MODEL`
2. 改 `chain.py` 把 `ChatOpenAI(...)` 換成 `ChatAnthropic(...)`，**或** 改用 `init_chat_model("anthropic:claude-...")` provider-agnostic 工廠

**金句**：「集中 config 是必要不充分 — 還要在 LLM 創建處用 `init_chat_model()` 才能真的 1 行切換。我目前用 `ChatOpenAI` 是 trade-off — production 我會用 `init_chat_model`。」

---

## 紅燈警報 🚨
Q9（reranker 故事）必須背熟 — 這是面試金牌素材。睡前讀 [week1_summary.md](week1_summary.md) 的「5 個面試核心 Soundbites」3 遍。

---

## 待答題（跳過的）
還沒答的 Q1（LCEL `|`）、Q3（chain vs agent）、Q5（chunk size 影響）、Q10（Recall vs MRR）、Q11（judge temperature=0 為什麼）— 之後想再考可以回來這份。
