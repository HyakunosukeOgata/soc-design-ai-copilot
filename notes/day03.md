# Day 3 收尾筆記 — Hybrid Retrieval + Reranker

> 日期：2026-04-24
> 今天完成：`hello_hybrid.py`（Semantic / BM25 / Hybrid / Hybrid+Rerank 四種比較）

---

## 一、必背 3 句 Production 金句

1. **RRF**：「按排名融合，自動避開兩邊 score 不可比。」
2. **Cross-encoder**：「query+doc 在 attention 層互相 attend，所以準但慢，只用於 top-N rerank。」
3. **架構**：「邏輯上分兩套、物理上一套——用 metadata filter + namespace 兼顧維運與隔離。」

---

## 二、面試 5 題深度 Q&A

### Q1. 純 semantic RAG 在 Verilog spec 上 retrieval 不準，怎麼循序漸進改進？

**順序很重要：先量化、從便宜的改起**

| Step | 動作 | 為什麼這個順序 |
|---|---|---|
| 1 | **建 eval set 跑 recall@k 拿 baseline** | 沒 baseline 不知道改進多少 |
| 2 | **Query rewriting / HyDE** | 最便宜，可能 query 端就有問題 |
| 3 | **Chunking 調整**（size、overlap、semantic chunking） | 不用換模型，調參數 |
| 4 | **Hybrid retrieval**（+BM25） | 補語意搜尋對冷僻 token 的盲點 |
| 5 | **加 Cross-encoder Rerank**（top-N → top-K） | 用 attention 重新審視 |
| 6 | **Fine-tune embedding / reranker** | 最貴，最後手段 |

**面試金句**：
> 「改進 RAG 的順序是『先量化、再從便宜的改起』。query rewriting 最便宜，fine-tune 最貴，順序反過來會浪費時間。」

---

### Q2. Hybrid weight 怎麼決定？為什麼 score 不能直接加？

**Weight 怎麼決定**：
- **不是憑感覺**——用 grid search（試 0.3 / 0.5 / 0.7…）跑 eval set 找最佳
- 經驗法則：技術文件 BM25 權重可以稍高（冷僻 token 多），通用文件 semantic 權重高

**為什麼不能直接加 score**：
- Embedding score 通常是 cosine similarity（[-1, 1]）
- BM25 score 是無上界的浮點數（可能 5、可能 50）
- **單位不可比**

**正確做法**：
1. **Min-max normalization** 把兩邊壓到 [0, 1] 再加權
2. **RRF (Reciprocal Rank Fusion)** ← 業界更常用
   ```
   RRF_score(d) = Σ 1 / (k + rank_i(d))
   ```
   只看排名不看 score，**完全跳過正規化問題**

LangChain 的 `EnsembleRetriever` **內建用 RRF**，weights 是當乘數權重。

---

### Q3. Reranker（cross-encoder）vs Embedding（bi-encoder）差別

| | Bi-encoder（embedding） | Cross-encoder（reranker） |
|---|---|---|
| **輸入** | query 跟 doc **分開**進模型 | query + doc **一起**進模型 |
| **輸出** | 兩個獨立向量 → cosine | 直接輸出 relevance score |
| **互動** | 兩邊**沒看到對方** | query 跟 doc 在 attention 層**互相看** |
| **速度** | 快（doc 可預先 embed） | 慢（每次都要重算） |
| **可預計算** | ✅ Doc 向量可入庫 | ❌ 必須當下算 |
| **用法** | 從百萬筆中粗篩 top-100 | 把 top-100 重排成 top-10 |

**為什麼 reranker 準**：
- query 跟 doc 在 transformer attention 層互相 attend
- 能捕捉細微相關性（"tradeoff" ↔ "the solution to that tradeoff"）
- bi-encoder 兩邊向量是**獨立壓縮**的，會丟細節

**為什麼 reranker 慢**：
- 每次 query 進來，對**每個 doc** 都要重跑一次 transformer
- 無法 pre-compute → 只能用在 top-N 的小池子

**面試金句**：
> 「標準 production 架構是 bi-encoder 粗篩 + cross-encoder 精排。Bi-encoder 速度快但細節流失，cross-encoder attention 互相 attend 所以準但慢。」

---

### Q4. Hybrid+Rerank 在某個 query 反而失敗，怎麼 debug？

**標準 debug 流程**：

1. **加 logging 看每階段**
   - 印出 hybrid 的 top-N（rerank 前）
   - 印出 reranker 的 score 排名
   - **關鍵問題**：rerank 前正確答案在不在 top-N？
     - 不在 → 上游問題（hybrid 沒抓到）
     - 在但被 reranker 降下去 → reranker 問題

2. **針對 reranker 問題**
   - **換 reranker 模型**：通用模型（如 ms-marco-MultiBERT）對 domain 不夠強，換 `bge-reranker-base`
   - **Fine-tune reranker**：用內部 query-doc 對訓練
   - **降低 reranker 影響**：top_n 設大一點不要砍太兇
   - **加 fallback**：reranker top-1 score 太低時退回 hybrid 結果

3. **針對 query 端**
   - Query rewriting：「energy usage of hash」→「power consumption of SHA-256 accelerator」

4. **加進 eval set**
   - 把這題納入 regression test
   - 下次改動立刻知道有沒有退步

**面試金句**：
> 「Production debug 順序：先 log → 確認哪階段壞掉 → 對症下藥 → 加進 eval 防 regression。最忌諱直接調參數但不知道為什麼。」

---

### Q5. 一套還是兩套 retrieval？（Verilog spec + 公司 SOP）

**結論**：**先一套 + metadata filter，必要時才拆**。

**先一套的理由**：
- Router classifier 本身會錯
- 維運成本（兩個 vector store、兩套 ingest pipeline、兩套監控）
- 部分 query 可能跨領域，分開反而漏

**什麼時候必須拆**：
| 情境 | 為什麼要拆 |
|---|---|
| **資料權限不同** | Verilog spec 公開、SOP 限部門 → 必須隔離 |
| **更新頻率差很大** | SOP 每月、spec 一年 → 分開 ingest 省成本 |
| **資料品質差很大** | spec 結構好、SOP Word 檔亂 → 切法不同 |
| **latency 要求差很大** | SOP 用 cache、spec 即時 |

**現代做法**：**單一 vector store + metadata filter + namespace**
```python
chroma.add(docs, metadatas=[
    {"type": "verilog_spec", "access": "public"},
    {"type": "sop", "access": "team_X"},
])
retriever.invoke(q, filter={"access": user.allowed})
```
**邏輯上分兩套，物理上一套**——兼顧維運與權限隔離。

**面試金句**：
> 「我會先單一 vector store + metadata filter，邏輯上分類但物理上一套，省維運。等到有強隔離（access control）或資料更新頻率明顯不同時才真的拆開。」

---

## 三、今天實作的 4 種 Retriever 對照（親手跑出來的數據）

| Query 類型 | Semantic | BM25 | Hybrid | Hybrid+Rerank |
|---|---|---|---|---|
| **概念性**（"clock crossing safely"）| ✅ 第 1 對 | ❌ 第 1 錯 | ⚠️ 第 1 錯 | ✅ **救回來** |
| **冷僻關鍵字**（"always_ff"）| ✅ 第 1 對 | ⚠️ 第 1 錯 | ✅ 第 1 對 | ✅ 第 1 對 |
| **同義詞**（"energy usage of hash"）| ✅ 第 1 對 | ❌ 第 1 錯 | ⚠️ 第 1 錯 | ❌ **反而更糟** |

### 我親身學到的 production 真相
1. **沒有單一最好的 retriever** — 看 query 類型
2. **Hybrid 默認 50/50 不一定好** — 弱的一邊會把 hybrid 拉下來
3. **Reranker 不是萬靈丹** — 通用 reranker 對 domain 場景可能反而錯
4. **必須跑 eval set 量化決定** — 不是哪個流行就用哪個

---

## 四、今天實際做了什麼

- [x] 裝 `rank-bm25`、`flashrank`
- [x] sample_spec.md 加 SystemVerilog 內容讓 BM25 有冷僻 token 可比
- [x] 寫 `hello_hybrid.py` 比較 4 種 retriever
- [x] 用 3 個對比 query（概念 / 關鍵字 / 同義詞）跑出差異
- [x] 觀察 reranker 在某個 query 反而失敗，理解通用 reranker 的限制

---

## 五、卡點 / 不懂的地方

-

---

## 六、明天 Day 4 預告

**主題**：Eval Pipeline — 把今天「靠眼睛看」的判斷，**自動化變成數字**

- 寫 golden Q&A set（15–20 題硬體題）
- 跑 retrieval recall@k
- LLM-as-judge faithfulness
- 比較 4 種 retriever 在 eval set 上的數字
- 這份報表將來能放進面試 demo（**面試官超愛看數字**）

---

## 七、給面試官 demo 時的講法（45 秒升級版）

> 「我做了 4 種 retriever 的對照實驗：純 semantic、純 BM25、Hybrid、Hybrid+Rerank。
>
> 用 3 種 query 類型測——概念性、冷僻關鍵字、同義詞——結果發現**沒有一招打天下**。
>
> 例如『energy usage of hash module』這題，純 semantic 第 1 名就對；但接上通用 cross-encoder reranker 反而被打亂——因為 ms-marco 那顆 reranker 沒看過硬體領域，聽不懂 energy = power。
>
> 這個實驗讓我學到三件事：第一，hybrid weight 不能憑感覺，要 grid search；第二，reranker 不是萬能，domain 場景可能要 fine-tune；第三，**所有判斷都要 eval set 量化**，這就是我下一步要做的。」

這段講完，面試官會知道你**真的踩過坑**、不是套教學。
