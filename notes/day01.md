# Day 1 收尾筆記 — LangChain 速成

> 日期：2026-04-23
> 今天完成：`test.py`（agent 版）+ `hello_chat.py`（chain 版）

---

## 一、5 題核心觀念

### Q1. LCEL 的 `|` pipe 在做什麼？

LCEL 的 `|` 是 LangChain 把 Unix pipe 概念帶到 LLM 應用。每個元件（`prompt` / `llm` / `parser`）都實作 **`Runnable` 介面**，所以可以用 `|` 自由組合。**pipe 左邊的 output 自動變成右邊的 input**。

```python
chain = prompt | llm | parser
#  dict → messages → AIMessage → str
```

**關鍵字**：Runnable、output 變 input、可組合。

---

### Q2. invoke / stream / batch 有什麼差別？什麼情境用哪個？

| 方法 | 行為 | 適用情境 |
|---|---|---|
| **invoke** | 同步呼叫，**等全部生成完**才回傳 | 一般 script、簡單呼叫 |
| **stream** | 同步呼叫，**邊生成邊吐 token** | Production chat UI、user 在等 |
| **batch** | **同時跑多個 input**（並行送 API） | 跑 eval set、批次處理 |

還有 async 版本：`ainvoke` / `astream` / `abatch`，在 FastAPI 這種 async 框架要用，避免 block event loop。

**面試金句**：
> 「invoke 是基礎；stream 是 production chat 必備，把 first-token-latency 從幾秒降到幾百毫秒；batch 並行送 API，跑 eval 100 題時遠比 for loop 快。」

---

### Q3. 什麼時候用 chain？什麼時候用 agent？

**Chain 適合**：
- 流程固定的任務（翻譯、摘要、RAG 問答、format 轉換）
- 不需要動態決策

**Agent 適合**：
- 需要呼叫 tool（查 API、讀檔、跑命令）
- 流程動態（要看上一步結果決定下一步）
- 多步驟推理 + 工具使用

**判斷原則**：
> **能用 chain 就用 chain**。Agent 的代價是 latency（每步 1 次 LLM call）、cost（token 累積快）、不可預測（可能 loop / 選錯 tool）。流程「動態 + 需要 tool」兩個都 yes 才用 agent。

---

### Q4. Streaming 為什麼對 production service 重要？

核心：**user 感受的不是「總時長」，是「等多久才看到第一個字」**。

| 模式 | First-token-latency | 全部生成 | User 感受 |
|---|---|---|---|
| `invoke` | 5 秒 | 5 秒 | 「卡住了？」 |
| `stream` | 0.3 秒 | 5 秒 | 「順順的，AI 在打字」 |

兩者**總時間一樣**，但體感完全不同。

**面試金句**：
> 「Production LLM service 一定要用 streaming。invoke 模式下 user 會以為 service 掛了；stream 把 first-token-latency 從幾秒降到幾百毫秒。實作上 FastAPI 用 SSE（Server-Sent Events）或 WebSocket 把 token 流式吐給前端。」

---

### Q5. System prompt 跟 user prompt 差別？

| | 用途 | 誰可改 |
|---|---|---|
| **system prompt** | 設定 LLM 的角色、能力範圍、輸出格式、guardrail | 開發者（user 看不到、改不了）|
| **user message** | user 的當下問題 | User |
| **assistant message** | LLM 的回答 | LLM 自動產生 |
| **tool message** | tool 執行結果 | 程式自動產生 |

**面試金句**：
> 「System prompt 是 LLM 行為的方向盤，user 看不到也改不了，所以可以放 sensitive instruction。但要小心 prompt injection——user 可能在 message 裡寫『忽略以上指令』，所以重要 guardrail 不能只靠 prompt，要在 service 層加 input/output validation。」

---

## 二、3 個情境快問快答

### 情境 1：RAG 問答系統 → **Chain** ✅
**為什麼**：流程固定（retrieve → 拼 context → 生成答案）。雖然有「外部資料」，但是**程式去拿**，不是 LLM 自己決定要不要拿。

> ⚠️ 進階：如果做 **Agentic RAG**（LLM 自己判斷要不要 retrieve、要 retrieve 什麼）那就變 agent。基礎 RAG 是 chain。

### 情境 2：「幫我訂明天 8 點的會議室」→ **Agent** ✅
**為什麼**：要用 tool（查行事曆、預訂 API）+ 動態決策（會議室被佔了要找替代方案）。

### 情境 3：翻譯 + 摘要兩步驟 → **Chain** ✅
**為什麼**：固定 2 步驟，串成 `chain = translate | summarize` 即可，不需要 LLM 「決定」要不要做這兩步。

---

## 三、今天實際做了什麼

- [x] 跑通 `test.py`（agent + 1 個 tool）
- [x] 跑通 `hello_chat.py`（chain，invoke / stream / batch 三種模式）
- [ ] 把 `test.py` 的 docstring 改空，觀察 agent 行為（選做）
- [ ] 改 `hello_chat.py` system prompt 風格（選做）
- [ ] 用 batch 跑 5 題比較 sequential vs batch 速度（選做）

---

## 四、卡點 / 不懂的地方

-

---

## 五、面試金句速記

- **LCEL**：「`|` 把 Unix pipe 帶進 LLM，元件實作 Runnable 介面就能組合。」
- **Stream**：「Production 一定 streaming，FTL 從幾秒降到幾百毫秒，user 體驗差很多。」
- **Chain vs Agent**：「能用 chain 就用 chain。Agent 代價是 latency + cost + 不可預測。」
- **Tool docstring**：「Tool 的 docstring 是 LLM 看的描述，寫不好 agent 會選錯 tool。」
- **System prompt**：「方向盤、user 改不了，但要防 prompt injection。」
