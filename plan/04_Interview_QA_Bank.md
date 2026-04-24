# 9 題技術問答範本（NVIDIA SOC AI Engineer）

## 使用方法

1. 每題有 **30 秒答（電梯版）** + **2 分鐘深答**
2. **不要背！** 用自己的話講出來，錄音聽 3 次
3. 面試時根據對方時間 / 表情切換版本
4. 每題結尾我都標了**「面試官最愛追問」**，要先想好答案

---

## 【RAG 類】

### Q1. 你怎麼決定 chunk size？對技術文件有什麼不同？

**30 秒版**：
> 「Chunk size 沒有銀彈，要看文件結構和 retrieval 目的。技術文件如 Verilog LRM 我會用 800–1000 chars + 100–150 overlap，因為段落結構長且有 cross-reference。如果是聊天紀錄就會用更小的 chunk。我的決策依據是『chunk 內要保留完整語意單元，但小到能讓 embedding signal 集中』。」

**2 分鐘版**：
> 「Chunk size 是 RAG 最關鍵也最被低估的參數。背後的 trade-off 是：
>
> - **太小**（< 200 chars）：embedding 會丟失上下文，retrieval 容易抓到片段，LLM 看不懂
> - **太大**（> 2000 chars）：embedding signal 被稀釋，多個概念混在一起，retrieval 精度下降
>
> 我的實際做法：
> 1. 看文件結構 → 技術文件用 RecursiveCharacterTextSplitter，按 `\n\n` → `\n` → 句號階層切
> 2. 設 chunk_size = 800、overlap = 120 是我對技術文件的起手式
> 3. **用 eval set 驗證**：跑 retrieval recall@5，調 chunk size 看曲線
> 4. 進階做法：semantic chunking（按句意切）或 parent-child（小 chunk 做 retrieve，回傳 parent 給 LLM）
>
> 對技術文件特別要注意 code block 和 table 不能被切斷，我會自訂 separator 保留這些結構。」

**面試官最愛追問**：
- 「你怎麼知道 800 是對的？」→ 答：跑 eval、recall@k 曲線
- 「Overlap 為什麼要 120 不是 0？」→ 答：避免關鍵句被切在邊界

---

### Q2. Retrieve 不到正確答案，你會怎麼 debug？

**30 秒版**：
> 「我會走 4 步：先看 query 本身（是否太模糊）、再看 chunking（答案是不是被切散了）、再看 embedding model 是不是抓得到語意、最後看是不是該用 hybrid search 補 BM25。每一步都用 eval set 量化，不靠感覺。」

**2 分鐘版**：
> 「Debug RAG retrieval 我有一個固定的 checklist：
>
> **Step 1：Query 端**
> - 問題太短或太籠統？→ 加 query rewriting / expansion / HyDE（用 LLM 先生成假答案再去 embed）
> - 問題用詞跟文件不同？→ 例如 user 問「register width」但文件寫「bit width」→ 需要 query expansion
>
> **Step 2：Chunking 端**
> - 答案是不是橫跨兩個 chunk？→ 增加 overlap 或改 semantic chunking
> - 答案在表格 / 程式碼裡？→ 改用結構感知的 splitter
>
> **Step 3：Embedding 端**
> - 試一下 BM25 baseline，如果 BM25 抓得到但 embedding 抓不到 → embedding model 對 domain 不夠強，考慮換 model 或 fine-tune
> - 反過來如果 embedding 抓得到但 BM25 抓不到 → query 用了同義詞
>
> **Step 4：Retrieval 策略**
> - 通常 hybrid (semantic + BM25) + reranker 是最穩的組合
> - reranker 我會用 bge-reranker-base，cross-encoder，對 top-20 重排成 top-5
>
> 最重要的是：**每一步都跑 eval set 量化**。我會維護一個 golden Q&A，固定看 recall@5、MRR 這兩個指標。」

**面試官最愛追問**：
- 「HyDE 是什麼？」→ Hypothetical Document Embeddings：用 LLM 生成一個假答案，把假答案 embed 去 retrieve
- 「Reranker 為什麼要用 cross-encoder？」→ Bi-encoder 是把 query / doc 各自 embed 算 cosine，cross-encoder 是 query+doc 一起進 model 輸出 relevance，精度高但慢，所以只用在 top-N rerank

---

### Q3. 怎麼評估 RAG 品質？

**30 秒版**：
> 「我分兩層評估：retrieval 層用 recall@k 和 MRR，generation 層用 faithfulness（LLM-as-judge 判斷答案是否 grounded）和 answer relevance。Golden set 至少 30 題，prompt 改版時自動 regression。」

**2 分鐘版**：
> 「RAG eval 要分兩層，混在一起會 debug 不出問題：
>
> **Retrieval Layer**
> - **Recall@k**：標準答案的來源 doc 在不在 top-k（最直接）
> - **MRR (Mean Reciprocal Rank)**：在 top-k 的第幾名（更精細）
> - **Context precision**：top-k 裡有多少是真的相關
>
> **Generation Layer**
> - **Faithfulness**：答案是不是只根據 retrieved context（防 hallucination），用 LLM-as-judge
> - **Answer Relevance**：答案有沒有真的回答問題
> - **Answer Correctness**：跟 golden answer 的語意相似度
>
> **End-to-end**
> - **Latency**：p50 / p95
> - **Cost per query**
>
> 工具上 Ragas 或 LangSmith Evaluation 都不錯，我會把這些指標跑進 CI，每次 prompt 或 retriever 改動自動跑 regression。
>
> 一個重要的 lesson：**LLM-as-judge 自己也會錯**，我會抽 10% 人工 review 校正 judge prompt。」

**面試官最愛追問**：
- 「Golden set 怎麼建？」→ 從真實 user query log 取樣 + 人工標註
- 「LLM-as-judge 不準怎麼辦？」→ 用更強模型做 judge、prompt 要明確、加 chain-of-thought、抽樣人工校正

---

## 【Agent 類】

### Q4. 為什麼用 Agent 不用單一 prompt？

**30 秒版**：
> 「當任務需要『動態決定下一步要做什麼』、需要呼叫外部工具、或需要 multi-turn reasoning，就該用 agent。如果任務是固定 pipeline 或單純 in-context 推理，single prompt 更便宜更快更可控。Agent 的代價是 latency、cost、和不可預測性。」

**2 分鐘版**：
> 「我判斷要不要用 agent 看 3 件事：
>
> **1. 路徑是否動態？**
> - 固定流程（先做 A 再做 B 再做 C）→ chain，不用 agent
> - 動態（要看上一步結果決定下一步）→ agent
>
> **2. 是否需要 tool？**
> - 純文字推理 → prompt 就夠
> - 需要查資料庫 / 跑 lint / call API → agent
>
> **3. 任務是否可拆？**
> - 一句話能描述輸入輸出 → prompt
> - 需要 multi-step plan → agent
>
> **Agent 的代價**（這段一定要講出來，顯示你不是盲目用 agent）：
> - **Latency**：每步至少一次 LLM call，5 步就是 5×latency
> - **Cost**：token 累積很快
> - **不可預測**：可能 loop、可能跑飛
> - **Debug 困難**：需要 tracing
>
> 所以我的原則是『**先用最簡單的方案，跑不動才升級到 agent**』。例如 RAG 問答能用 single chain 就不用 agent。」

**面試官最愛追問**：
- 「什麼時候用 LangGraph 不用 LangChain Agent？」→ 需要明確控制 state machine、需要 cycle、需要 human-in-the-loop 時用 LangGraph

---

### Q5. Agent 跑飛了 / 無限迴圈怎麼辦？

**30 秒版**：
> 「四道防線：硬上限（max_steps、max_tokens、max_cost）、loop detection、tool failure handling、human-in-the-loop。設計 agent 時 guardrail 跟 prompt 一樣重要。」

**2 分鐘版**：
> 「我會設四層 guardrail：
>
> **第一層：硬性上限**
> - `max_steps = 10`
> - `max_tokens_per_step = 2000`
> - `total_cost_cap_usd = 0.10`
> - 超過直接 abort 並回 partial result
>
> **第二層：Loop detection**
> - 偵測連續 N 步呼叫同一個 tool 同樣 input → 強制 break
> - 偵測 thought 重複 → 提示 agent 換策略
>
> **第三層：Tool 失敗處理**
> - Tool 拋例外 → catch 後當 observation 餵回給 agent
> - 連續 retry 失敗 → fallback 路徑（例如：lint tool 跑不起來，改建議『請手動確認』）
>
> **第四層：Human-in-the-loop**
> - 高風險動作（會修改檔案、會花錢、會送出資料）→ 強制要 user confirm
> - LangGraph 的 `interrupt` 很適合這個
>
> 加分：**observability**。我會每步都 log structured event（step number、thought、tool、tool_input、observation、latency、tokens），事後可 replay。LangSmith 內建這個，自寫也不難。」

**面試官最愛追問**：
- 「Human-in-the-loop 怎麼做？」→ LangGraph interrupt、或在 tool 內 raise 一個 ApprovalRequired 例外
- 「怎麼知道要用 max_steps = 10 不是 20？」→ 看 eval set，95% 任務在 N 步內完成 → 設 N+2

---

### Q6. Tool 的 schema 怎麼設計？

**30 秒版**：
> 「Tool 設計三原則：name 動詞開頭描述行為、docstring 要寫『何時用』而不只是『做什麼』、輸入輸出 schema 用 pydantic 並包含範例。LLM 選錯 tool 通常是 docstring 寫不好。」

**2 分鐘版**：
> 「Tool 設計 LLM 友善程度直接決定 agent 品質。我的 checklist：
>
> **Naming**
> - 動詞開頭：`search_docs`、`run_lint`、`fetch_register_spec`
> - 不要用縮寫
>
> **Docstring（最重要）**
> - 寫「**何時該用**」+「**何時不該用**」
> - 範例：`"""Search Verilog LRM for syntax/semantics. Use when user asks about language rules. DO NOT use for OpenTitan-specific questions."""`
>
> **輸入 schema**
> - 用 pydantic BaseModel 明確型別
> - 必填參數放前面，optional 放後面
> - 加 description：`Field(..., description="Verilog code as a string")`
>
> **輸出**
> - 結構化 > 純文字
> - 失敗時回有意義的錯誤訊息（給 LLM 讀的）：`"Error: file not found at path X. Suggestion: check spelling."`
> - 不要回 raw exception
>
> **冪等性**
> - Tool 應該設計成可重複呼叫（agent 可能 retry）
> - 有副作用的 tool 要明確標註並考慮 confirm 機制
>
> **常見錯誤**：tool 太多（>15 個 LLM 會選錯）→ 拆 sub-agent 或 hierarchical tool。」

**面試官最愛追問**：
- 「Tool 太多怎麼辦？」→ Tool grouping、retrieval-based tool selection（先 retrieve top-5 tool 再讓 agent 看）

---

## 【Service / Production 類】

### Q7. LLM service 怎麼處理 latency？Streaming 怎麼做？

**30 秒版**：
> 「Latency 我從三層下手：model 端用 streaming + 較小 model + KV cache、retrieval 端用 batch embedding + cache、network 端用 async + connection pool。Streaming 用 FastAPI 的 SSE 或 WebSocket，把 token 流式吐給前端，user perceive latency 大幅下降。」

**2 分鐘版**：
> 「LLM service 的 latency 來自三段：retrieval、LLM inference、network。
>
> **Retrieval 優化**
> - Embedding query batch + async
> - 熱門 query 結果 cache（Redis）
> - Vector DB 用 HNSW index 快速近似
>
> **LLM inference 優化**
> - **Streaming 是必做**：first-token-latency 從 3s 降到 300ms
> - 選對模型大小：簡單任務用 small model
> - Prompt caching（OpenAI / Anthropic 都有）對長 system prompt 有效
> - Speculative decoding / batching（如果 self-host）
>
> **Service 層**
> - FastAPI 全 async（avoid blocking IO）
> - LLM client 用 connection pool
> - 並發控制：rate limiter 防 overload
>
> **Streaming 實作**
> ```python
> from sse_starlette.sse import EventSourceResponse
>
> @app.post('/ask')
> async def ask(req: Query):
>     async def gen():
>         async for chunk in chain.astream(req.question):
>             yield {'data': chunk}
>     return EventSourceResponse(gen())
> ```
>
> **量測**
> - 一定要分 first-token-latency 和 total-latency 看
> - p50 / p95 / p99 都要追，user 看的是 p95」

**面試官最愛追問**：
- 「Streaming 中間錯了怎麼辦？」→ 在 stream event 加 type 欄位，前端可處理 `error` event
- 「怎麼支援 cancel？」→ FastAPI 偵測 client disconnect，cancel 上游 LLM call

---

### Q8. Prompt 怎麼版本控制？Regression test 怎麼設計？

**30 秒版**：
> 「Prompt 我把它當 code 管：放 git、PR review、有 version tag。Regression test 是固定 N 題 golden set，每次 prompt 改動自動跑，比對指標 delta，超過閾值就 block PR。」

**2 分鐘版**：
> 「Prompt 是 LLM 系統最常變動也最容易壞的部分，我的做法：
>
> **Prompt 版本控制**
> - Prompt 放在獨立檔案（不是 hardcode 在 Python）
> - 用 LangChain Hub 或自寫 `prompts/v1.txt`
> - Git commit + tag，每個 deploy 對應明確 version
> - 進階：prompt registry（DB 存版本，可線上切換 A/B）
>
> **Regression test 設計**
> - **Golden set**：30–100 題標準 Q&A，涵蓋 happy path + edge case + adversarial
> - **CI 整合**：PR 觸發跑 eval，產出指標 diff
> - **Threshold**：核心指標（faithfulness、recall）下降 > 3% 自動 block
> - **Cost / latency**：也要 track，避免 prompt 越改越長
>
> **Prompt change 流程**
> 1. 開 branch 改 prompt
> 2. local 跑 eval 看數字
> 3. PR 自動跑 full eval，產出對照表
> 4. Reviewer 看數字 + qualitative diff
> 5. Merge 後 canary 部署
>
> **常見坑**
> - Golden set 太小 → 統計不顯著，至少 30 題
> - 只看 aggregate 不看 per-case → 可能整體不變但特定 case 退化
> - LLM-as-judge 自己會 drift → 定期人工校驗」

**面試官最愛追問**：
- 「Golden set 維護成本高怎麼辦？」→ 從 production log 半自動標註、用 LLM 預標再人工 review
- 「prompt A/B test 怎麼做？」→ Feature flag 分流、看線上 metric

---

### Q9. On-prem 部署 LLM 服務要注意什麼？（你前公司有 proprietary data，這題很適合接）

**30 秒版**：
> 「On-prem 三大關卡：模型選型（open weight 如 Llama / Qwen）、資料隱私（all in VPC、不能 call external API、log 要 PII scrub）、運維（GPU 排程、可觀測性、版本管理）。NVIDIA 這個職缺講 proprietary data 我特別有共鳴，因為前公司也是封閉環境。」

**2 分鐘版**：
> 「On-prem LLM service 跟 SaaS 模式很不一樣，幾個重點：
>
> **模型選型**
> - 不能用 OpenAI / Claude API → 用 open weight：Llama 3、Qwen 2.5、Mistral
> - 部署 framework：vLLM（高吞吐）、TGI、Ollama（dev 用）
> - Embedding 也要 self-host：bge / e5 系列
>
> **資料隱私 / 安全**
> - 所有 data flow 留在 VPC / 內網
> - LLM call log 要 PII scrub（regex + LLM-based detection）
> - Vector DB 加 access control（per-team / per-project namespace）
> - Prompt injection 防護：input sanitization、output validation
> - 不允許 LLM 主動 call external（除非允許清單）
>
> **運維**
> - GPU 排程：K8s + GPU operator，或 Slurm
> - 模型 update：blue-green deploy，避免 downtime
> - 可觀測性：Prometheus + Grafana 看 GPU util、LLM latency、token throughput
> - Disaster recovery：vector DB 有 backup、prompt registry 有 backup
>
> **成本控制**
> - GPU 是最大開銷 → batch、quantization (INT8 / AWQ)、speculative decoding
> - 我前公司的 LLM-EDA 工具就是內網部署，所以這些痛點我都有實際碰過。」

**面試官最愛追問**：
- 「prompt injection 怎麼防？」→ Input filtering、output guardrail（不准執行特定指令）、separate user/system role、結構化 input
- 「vLLM 為什麼比 transformers 快？」→ PagedAttention 管 KV cache、continuous batching

---

## 通用答題框架（所有題目都適用）

### 「STAR-T」結構
1. **答結論**（1 句）
2. **三點論述**（用編號 / first-second-third）
3. **舉例**（說一個你做過的具體場景）
4. **Trade-off / 反思**（顯示你不是只會單一答案）

### 三大加分動作
1. ✅ 主動提到 **trade-off**：「這個方案的代價是 ___」
2. ✅ 提到 **量化 / 評估**：「我會用 ___ 指標來驗證」
3. ✅ 連到 **你做過的事**：「我在 Fitipower / 我的 side project 就是這樣做」

### 三大致命動作
1. ❌ 不知道硬猜：「我覺得應該是 ___ 吧」← 不如說「這個我沒實際做過，但根據 ___ 原理我推測 ___」
2. ❌ 答案太短沒展開：一句話結束
3. ❌ 答案太長沒重點：講 5 分鐘還沒進入主題

---

## 練習方式

### 第一輪（自答）
- 對著鏡頭錄影，每題 2 分鐘
- 回放找出：贅字、口頭禪、目光、結構

### 第二輪（壓力測試）
- 找朋友 / ChatGPT 隨機抽題，限時 90 秒
- 要能立刻進入主題

### 第三輪（追問）
- 每題追問 2 層：「為什麼」「怎麼證明」
- 答不出來的點寫進 follow-up list 補強
