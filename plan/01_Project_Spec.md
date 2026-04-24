# Killer Project 技術規格

## 專案名稱
**SOC Design AI Copilot** (建議 GitHub repo 名: `soc-design-ai-copilot`)

## 一句話定位
> 一個給 SOC / RTL 工程師用的 AI 助手服務：用 RAG 回答硬體設計文件問題，用 Agent 自動分析與修復 RTL lint 錯誤。

## 為什麼這個題目
- 涵蓋 JD 三大支柱：**LLM Service + RAG + Agent**
- 題材是**硬體領域**，與 NVIDIA SOC team 的 user 完全對齊
- 你能講硬體細節，面試官問下去你不會啞口
- 涵蓋「reusable skill / playbook」概念（對應 JD 的 Claude Code-style）

---

## 系統架構

```
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Service                        │
│                                                          │
│  POST /ask        ──► RAG Pipeline ──► LLM ──► Stream   │
│  POST /agent      ──► Agent Executor ──► Tools          │
│  GET  /health                                            │
│  GET  /eval/report                                       │
└─────────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
   ┌──────────┐         ┌──────────────┐
   │ Chroma   │         │ Tools:       │
   │ Vector DB│         │ - grep_rtl   │
   └──────────┘         │ - lookup_spec│
         ▲              │ - run_lint   │
         │              └──────────────┘
   ┌──────────┐
   │ Embedding│
   │ Model    │
   └──────────┘
         ▲
         │
   ┌──────────┐
   │ Hardware │
   │ Docs     │  (Verilog LRM, OpenTitan, Ibex, RISC-V spec)
   └──────────┘
```

---

## 檔案結構

```
soc-design-ai-copilot/
├── README.md                  # 必須漂亮、有架構圖、有 demo gif
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── data/                      # 硬體文件原始檔
│   ├── verilog_lrm/
│   ├── opentitan_docs/
│   └── riscv_spec/
│
├── src/
│   ├── __init__.py
│   ├── config.py              # pydantic-settings
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingest.py          # 文件 → chunk → embed → Chroma
│   │   ├── retriever.py       # retrieve + rerank
│   │   └── chain.py           # LCEL chain
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── tools.py           # grep_rtl / lookup_spec / run_lint
│   │   ├── executor.py        # LangChain AgentExecutor
│   │   └── prompts.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app
│   │   ├── schemas.py         # pydantic request/response
│   │   └── streaming.py       # SSE / streaming
│   │
│   └── observability/
│       ├── __init__.py
│       └── logging.py         # structured log + trace
│
├── skills/                    # ★ Claude Code-style reusable skills
│   └── rtl_lint_fix/
│       ├── SKILL.md
│       └── prompt.md
│
├── eval/
│   ├── golden.jsonl           # 15-20 題標準 Q&A
│   ├── run.py                 # 跑 retrieval recall@k + LLM-as-judge
│   └── reports/               # 結果存這裡
│
├── tests/
│   ├── test_retriever.py
│   ├── test_tools.py
│   └── test_api.py
│
└── notebooks/
    └── exploration.ipynb      # 開發過程記錄
```

---

## API 規格

### `POST /ask`
RAG 問答（streaming）

**Request**
```json
{
  "question": "What is the difference between blocking and non-blocking assignment in Verilog?",
  "top_k": 5,
  "stream": true
}
```

**Response (SSE)**
```
data: {"type": "retrieval", "docs": [{"source": "verilog_lrm.pdf", "page": 142, "score": 0.87}, ...]}
data: {"type": "token", "content": "In Verilog, "}
data: {"type": "token", "content": "blocking assignment "}
...
data: {"type": "done", "trace_id": "abc123"}
```

### `POST /agent`
Agent 模式（multi-step）

**Request**
```json
{
  "task": "Review this RTL and fix any lint warnings",
  "rtl_code": "module foo(...); ... endmodule",
  "max_steps": 10
}
```

**Response**
```json
{
  "trace_id": "xyz789",
  "steps": [
    {"step": 1, "thought": "...", "tool": "run_lint", "tool_input": "...", "observation": "..."},
    {"step": 2, "thought": "...", "tool": "lookup_spec", ...}
  ],
  "final_answer": "...",
  "fixed_rtl": "..."
}
```

### `GET /health`
標準 health check

### `GET /eval/report`
回傳最近一次 eval 結果（recall@k、faithfulness 分數）

---

## RAG 設計細節

| 元件 | 選擇 | 為什麼 |
|---|---|---|
| Embedding | `BAAI/bge-small-en-v1.5` (or OpenAI `text-embedding-3-small`) | 開源 / 便宜，技術文件表現好 |
| Vector DB | Chroma | 最簡單、檔案 mode 不用另起服務 |
| Chunking | RecursiveCharacterTextSplitter, chunk_size=800, overlap=120 | 技術文件 paragraph 較長 |
| Retrieval | Hybrid: semantic top-k + BM25 top-k → merge | 技術術語 BM25 很重要 |
| Rerank | (optional) `BAAI/bge-reranker-base` | 加分，面試講出來會更深 |
| LLM | OpenAI gpt-4o-mini / Claude / Ollama (qwen2.5) | 看你 budget |

**面試會被問到的點**（你要能回答）：
- 為什麼 chunk_size = 800？→ Verilog LRM 段落結構，太小會切斷上下文，太大會稀釋 embedding signal
- 為什麼要 hybrid？→ 技術文件有大量 keyword（`always_ff`, `tristate`），純 semantic 會 miss
- 怎麼防 hallucination？→ Prompt 強制「只能根據 context 回答 + 引用 source + 不知道就說不知道」

---

## Agent 設計細節

### Tools
```python
@tool
def grep_rtl(pattern: str, file_path: str) -> str:
    """Search for a regex pattern in an RTL file. Returns matching lines with line numbers."""

@tool
def lookup_spec(query: str) -> str:
    """Look up Verilog/SystemVerilog spec via RAG. Use for syntax/semantics questions."""

@tool
def run_lint(rtl_code: str) -> str:
    """Run a (mock) lint tool on RTL code. Returns warnings and errors."""
    # Mock 即可，重點不是真的 lint，是展示 tool integration
```

### Guardrails（**面試大加分**）
- `max_steps = 10`
- `max_tokens_per_step = 2000`
- `total_cost_cap_usd = 0.10`
- 每個 tool call 失敗自動 retry 1 次後 fallback
- 如果 agent 偵測到 confidence 低 → 回 "需要 human review"

---

## Eval 設計

### Golden set 範例（`eval/golden.jsonl`）
```json
{"id": "q001", "question": "What is the difference between `wire` and `reg` in Verilog?", "expected_keywords": ["continuous", "procedural", "always block"], "expected_source": "verilog_lrm.pdf"}
{"id": "q002", "question": "How does OpenTitan implement secure boot?", "expected_keywords": ["ROM", "OTP", "key manager"], "expected_source": "opentitan_docs"}
```

### Metrics
1. **Retrieval recall@5**：標準答案來源 doc 是否在 top-5
2. **LLM-as-judge faithfulness**：用 GPT-4 判斷答案是否「只根據 context」
3. **Answer relevance**：用 GPT-4 判斷答案是否真的回答問題
4. **Latency p50/p95**

### 報表（Markdown）
跑完 `python eval/run.py` 自動生成 `eval/reports/2026-04-23.md`，內容：
| Metric | Score |
|---|---|
| Retrieval recall@5 | 0.85 |
| Faithfulness | 0.92 |
| Answer relevance | 0.88 |
| Latency p50 | 1.3s |

---

## Reusable Skill 範例（對應 JD 的 Claude Code-style）

`skills/rtl_lint_fix/SKILL.md`
```markdown
# Skill: RTL Lint Fix

## Purpose
Given an RTL file with lint warnings, classify them and propose fixes.

## When to use
- User pastes RTL with lint output
- User asks "fix this lint warning"

## Procedure
1. Run `run_lint` tool on the RTL
2. For each warning, call `lookup_spec` to find the relevant rule
3. Generate a patch with explanation
4. If warning is in deprecated category, suggest modernization

## Guardrails
- Never modify port declarations without explicit user confirmation
- Always preserve original comments
```

---

## Dockerfile（簡化版）
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .
COPY src/ src/
COPY skills/ skills/
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## docker-compose.yml
```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db
```

---

## README 必備內容（**這份決定面試官的第一印象**）

1. 一段話 elevator pitch
2. **架構圖**（用 mermaid 或截圖）
3. Demo GIF / 影片連結
4. Quick start（3 行 docker-compose up）
5. API 範例（curl）
6. Eval 結果表格
7. Design decisions（為什麼用 Chroma 不用 Pinecone、為什麼 hybrid retrieval...）→ **這段是面試官最愛看的**
8. Roadmap（誠實寫「下一步想加什麼」，例如：權限控管、multi-tenant）

---

## 完成定義（Definition of Done）

- [ ] `docker-compose up` 任何人 clone 後 5 分鐘能跑起來
- [ ] `/ask` endpoint 能 streaming 回答硬體問題
- [ ] `/agent` endpoint 能 multi-step 處理 RTL 任務
- [ ] `eval/run.py` 能產出可讀的報表
- [ ] README 有架構圖 + demo
- [ ] 至少 1 個 `skills/*/SKILL.md`
- [ ] 至少 5 個 unit test 過
- [ ] LangSmith trace（或自寫 log）能秀給面試官看
