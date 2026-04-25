# Day 8 — FastAPI Service: RAG 變成真服務

## 今天做了什麼
把 RAG pipeline 從 script 包成 FastAPI HTTP service，含 SSE streaming。

### 產出
- `src/soc_copilot/api/`
  - `main.py` — FastAPI app（`/ask`, `/ask/stream`, `/health`）
  - `schemas.py` — Pydantic request/response models
  - `cli.py` — uvicorn launcher
- `tests/test_api.py` — 4 個 smoke tests（全 pass）
- README 更新含 curl 範例

---

## 3 個 Endpoints

| Endpoint | Method | 回 | 用途 |
|---|---|---|---|
| `/health` | GET | `{status, chunks_indexed}` | LB / k8s probe |
| `/ask` | POST | `{answer, sources[], refused}` | 同步問答 |
| `/ask/stream` | POST | SSE token stream | Chatbot UX |

---

## 設計決策（要能講）

### 1. Lifespan-based startup（不在每次 request load）
```python
@asynccontextmanager
async def lifespan(app):
    chunks, vs = build_index()        # 只跑一次
    _state["chain"] = make_rag_chain(...)
    yield
```
- **如果不這樣**：每個 request 都會重新 embed 整個 corpus → P99 latency 爆炸
- **正確做法**：startup 一次性建索引，request 共用 module-level state
- 面試金句：「FastAPI lifespan 是 production RAG 必備 — index build 屬於 startup cost，不是 request cost」

### 2. 為什麼 `/ask` 回 sources 而不只回 answer
```json
{
  "answer": "...",
  "sources": [{"content": "...", "chunk_id": 0}],
  "refused": false
}
```
- **Production RAG 一定要 cite sources** — user 要能 verify、debug、追責
- `refused` 欄位讓前端可以 render 不同 UI（拒答 vs 答案）
- 面試金句：「無 source 的 RAG 答案 = 黑盒 — production 不能用」

### 3. SSE 不用 WebSocket
- SSE 單向（server→client）夠用
- HTTP 標準，nginx / CDN / 公司 proxy 都友善
- WebSocket overhead 大，雙向通常 chatbot 不需要

### 4. 用 `astream` 而非 `stream`
- `astream` = async generator → 一個 worker 同時服務 N 個 user 邊吐 token
- `stream` = sync → 一個 worker 一次只能服務一個 user
- **這就是 invoke/stream/batch 還要 ainvoke/astream/abatch 的原因**

### 5. 為什麼要 escape `\n`
```python
safe = token.replace("\n", "\\n")
yield f"data: {safe}\n\n"
```
- SSE 用 `\n\n` 當 event boundary。token 自己含 `\n` 會把 SSE frame 切爆
- 不踩這個坑 = 生產等級細節

---

## 採坑紀錄

### Bug 1: PowerShell 跑 `copilot-serve.exe` 被 AppLocker 擋
- Windows 應用程式控制原則封鎖 .exe entry point
- 修：改用 `python -m uvicorn soc_copilot.api.main:app`

### Bug 2: `curl.exe` 在 PowerShell 中 JSON quoting 慘
- 雙引號 escape 一團亂 → server 收到 `{}` 報 422
- 修 1：用 `Invoke-RestMethod` + `ConvertTo-Json`（PowerShell native）
- 修 2：用 `curl.exe --data-raw '{...}'` 單引號保護

---

## Tests
```
tests/test_api.py::test_health PASSED
tests/test_api.py::test_ask_in_scope PASSED
tests/test_api.py::test_ask_out_of_scope_refuses PASSED
tests/test_api.py::test_ask_validation_empty_question PASSED
============= 4 passed in 15.75s =============
```

`TestClient` 自動觸發 lifespan → 不需 mock，等同跑真 server。

---

## 面試 Soundbites

### 「你 RAG 怎麼上 production？」
> 「FastAPI app + lifespan startup 建索引 + `/ask` 回 sources + `/ask/stream` 用 SSE 吐 token + Pydantic 做 input validation。Index 屬於 startup cost、astream 用 async generator 支援多 user 並發、SSE event 要 escape `\n` 否則會切碎 frame。」

### 「為什麼 SSE 不用 WebSocket？」
> 「Chatbot 是單向 server-to-client，SSE 夠。SSE 是純 HTTP，nginx / CDN / 公司 proxy 全部友善；WebSocket 要額外設 upgrade，企業 firewall 常擋。」

### 「Pydantic 帶來什麼價值？」
> 「Free input validation — `min_length=1, max_length=1000` 一行寫完，亂打空字串自動回 422 而不是讓我的 chain 炸。Schema 也讓 OpenAPI / Swagger UI 自動生，前端可直接看 contract。」

---

## Day 8 Done ✅
明天 Day 9：Agent layer，加 RTL lint + spec lookup tools。
