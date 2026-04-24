# Day 2 收尾筆記 — RAG 基礎 + Hybrid 概念

> 日期：2026-04-23
> 今天完成：`hello_rag.py`（完整 RAG pipeline）+ chunk size 實驗 + hybrid 概念

---

## 一、面試必考：RAG 5 大金句

| # | 主題 | 一句話金句 |
|---|---|---|
| 1 | RAG 是什麼 | 「Retrieve 相關文件 → Augment 進 prompt → LLM Generate，讓 LLM 不靠記憶現查現答。」 |
| 2 | Embedding | 「把文字映射到高維空間，語意相近的文字向量靠近。Retrieval 本質就是 query 向量找最近的 doc 向量。」 |
| 3 | Chunking | 「太小失去上下文、太大稀釋 embedding signal。技術文件起手式 800/120，要用 eval set 驗證。」 |
| 4 | Hybrid | 「Embedding 抓語意、BM25 抓關鍵字。技術文件兩邊互補，hybrid 增益最大。」 |
| 5 | Stuff vs RAG | 「文件總量 < context window 直接 stuff 就好，不要為了用 RAG 而用 RAG。」 |

---

## 二、面試 Q&A（深度版）

### Q1. RAG 的完整 pipeline 有哪幾步？

```
[Ingest 階段 — 一次性]
原始文件 → Loader → Splitter → Embedding → Vector Store

[Query 階段 — 每次問問題]
user query → Embedding → Vector Store 找 top-K → 塞進 prompt → LLM → answer
```

**5 個零件 + 對應工具**：
| 零件 | 範例 | 我用的 |
|---|---|---|
| Loader | PyPDFLoader / TextLoader | TextLoader |
| Splitter | RecursiveCharacterTextSplitter | chunk_size=400, overlap=60 |
| Embedding | text-embedding-3-small / bge | text-embedding-3-small |
| Vector Store | Chroma / Qdrant / Milvus | Chroma（記憶體模式）|
| Retriever | semantic / BM25 / hybrid | as_retriever(k=3) |

---

### Q2. Chunk size 怎麼決定？

**答題框架**：
1. **沒有銀彈**，看文件結構與 retrieval 目的
2. **太小（< 200）**：語意被切斷，retrieve 抓到片段
3. **太大（> 2000）**：embedding signal 稀釋，多個概念混在一起
4. **技術文件**：800 / overlap 120 是起手式
5. **唯一決定方法**：跑 eval set，看 recall@k 曲線

**我實際做過的實驗**：
- chunk_size=100：chunks 從 8 → 32，碎片化
- chunk_size=5000：chunks → 1，已經不是 RAG 是 stuff method

**進階加分**：semantic chunking（按句意切）、parent-child（小 chunk retrieve、回傳 parent）

---

### Q3. Embedding 是什麼？為什麼能做 retrieval？

> 「Embedding 模型把文字轉成高維向量（OpenAI text-embedding-3-small 是 1536 維）。模型在訓練時學到『語意相近的文字 → 向量在空間中靠近』。
>
> Retrieval 就是把 query 也 embedding 化，跟資料庫中所有 doc 向量算 cosine similarity，回傳距離最近的 top-K。
>
> Vector store 用 ANN（如 HNSW）建索引，讓百萬級向量也能毫秒級查詢。」

---

### Q4. Retrieve 不到正確答案，怎麼 debug？

**4 步檢查法**：
1. **Query 端**：query 太模糊？→ query rewriting / HyDE / query expansion
2. **Chunking 端**：答案橫跨兩 chunk？→ 增加 overlap / semantic chunking
3. **Embedding 端**：跑 BM25 baseline，BM25 抓到但 embedding 沒抓到 → 模型對 domain 不夠強
4. **Strategy 端**：用 hybrid + reranker

**重要原則**：每一步都用 eval set 量化，不靠感覺。

---

### Q5. 什麼時候 RAG 不適用？該用什麼？

| 情境 | 不該用 RAG，該用 ___ |
|---|---|
| 文件 < 50 頁 / 全部 < 100k token | **Stuff method**（直接整份塞進 prompt）|
| 需要跨文件統計 / 數值聚合（「總共幾篇文章提到 X」）| **Text-to-SQL** + 結構化資料 |
| 需要動態決策 / multi-step（「先查 A 再依 A 查 B」）| **Agentic RAG**（retriever 包成 tool 給 agent）|
| 知識會頻繁更新 / 即時資料 | **Tool calling** 直接呼叫 API |

**面試金句**：「RAG 不是萬靈丹。先看資料量、查詢模式、更新頻率，再決定要不要用。」

---

### Q6. Hybrid Retrieval 是什麼？怎麼做？

**為什麼要 hybrid**：
- 純 semantic：抓「意思相近」，但**漏關鍵字 / 冷僻 token**
- 純 BM25：抓「字面相同」，但**漏同義詞**
- 兩者**互補**

**架構**：
```
       query
      ↙       ↘
semantic     BM25
top-K       top-K
      ↘       ↙
    merge / RRF
         ↓
    (optional) reranker
         ↓
      final top-K
```

**結果合併方法**：
1. **RRF (Reciprocal Rank Fusion)**：按排名合併，不看原始 score（最常用）
2. **加權平均**：要先正規化 score
3. **Cross-encoder reranker**：把 top-N 重排（最精準但最慢）

**面試金句**：「Hybrid 結果合併不能直接加 score，因為兩邊 score 單位不可比。RRF 按排名 fuse 是最穩的做法。技術文件做 hybrid 增益最大。」

---

### Q7. RAG 怎麼防 hallucination？

**4 道防線**：
1. **Prompt 強制**：「Answer ONLY based on context. If not found, say I don't know.」
2. **Source citation**：要 LLM 引用原文句子（user 可驗證）
3. **Faithfulness eval**：用 LLM-as-judge 自動檢查答案是否 grounded
4. **Confidence threshold**：retrieve 的最高 score 太低 → 直接拒答

**我做過的**：
- 在 hello_rag.py prompt 寫了 "ONLY based on context"
- 問 NVIDIA H100 價格 → 文件沒寫 → 老實回 "I don't know"

---

### Q8. RAG 怎麼評估品質？

**兩層 metrics**：

**Retrieval 層**
- `Recall@k`：標準答案的來源 doc 是否在 top-k
- `MRR`：在 top-k 的第幾名
- `Context precision`：top-k 裡有多少真的相關

**Generation 層**
- `Faithfulness`：答案是否只根據 context（防 hallucination）
- `Answer relevance`：是否真的回答問題
- `Answer correctness`：跟 golden answer 的相似度

**End-to-end**
- Latency p50 / p95
- Cost per query

**工具**：Ragas、LangSmith Evaluation

---

### Q9. Vector Store 該怎麼選？

| 選項 | 適合 |
|---|---|
| Chroma | 開發 / 小規模，檔案模式不用另起服務 |
| Qdrant | 中大型 production，open source 自架 |
| Pinecone | SaaS、不想自己維運 |
| Milvus / Weaviate | 大規模、多租戶 |
| pgvector | 已經用 Postgres 想省一個服務 |

**面試金句**：「沒有最好的，看 scale + 維運成本。我 dev 用 Chroma 簡單，production 會評估 Qdrant 自架，因為 NVIDIA proprietary data 不能上 SaaS。」

---

## 三、我今天實際做了什麼

- [x] `hello_rag.py` 跑通完整 5 步 pipeline
- [x] 實驗 1：chunk_size=100 → 8 chunks 變 32，發現碎片化
- [x] 實驗 2：chunk_size=5000 → 變成 1 chunk，理解這時已經不是 RAG 是 stuff
- [x] 實驗 3：prompt 加 "Source:" 引用 → 答案會多一行 source
- [x] 理解 Embedding + Vector Store 的運作原理
- [x] 理解 Hybrid (semantic + BM25) 為什麼互補

---

## 四、卡點 / 不懂的地方

-

---

## 五、明天 Day 3 預告

- 實作 Hybrid Retrieval（用 EnsembleRetriever）
- 親眼比較：純 semantic / 純 BM25 / hybrid 抓到的差別
- 加 reranker（cross-encoder）

---

## 六、給面試官 demo 時的講法

> 「我這個 RAG 系統用了 5 個零件：TextLoader 載 markdown，RecursiveCharacterTextSplitter 切成 800 字 chunks（120 overlap），text-embedding-3-small 做 embedding 存到 Chroma。Retrieval 用 hybrid（semantic + BM25），對技術文件特別重要，因為 Verilog 關鍵字單純 embedding 抓不到。Prompt 我強制要求 only based on context 並要求引用原文，所以答案可驗證、不會 hallucinate。Eval 我用 Ragas 跑 faithfulness 和 recall@k。」

這段 60 秒講完，面試官就知道你**真的做過 RAG**，不是只會背名詞。
