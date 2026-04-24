# 面試準備作戰計畫（NVIDIA SOC AI Engineer / JR2016498）

## 你的現況盤點

| 項目 | 狀態 | 策略 |
|---|---|---|
| 階段 | 內推剛送出，**還沒排面試** | 有時間從容準備，**不用急但要穩** |
| 每日投入 | 3 hr | 約等於每週 21 hr，是充裕的 |
| FastAPI | ✅ 用過 | 不用學，直接用 |
| RAG | 🟡 用過但不深 | **重點補強對象** |
| LangChain | 🔴 沒實作過 | **必補**，但不用變專家 |

**好消息**：內推到排面試通常 1–4 週，你有時間做出一個漂亮的 demo project。

---

## 三週作戰計畫（21 天 × 3hr ≈ 63 小時）

### 🟢 Week 1：建基底（補 LangChain + 強化 RAG）

| Day | 主題 | 任務 (3hr) | 產出 |
|---|---|---|---|
| 1 | **LangChain 速成** | 跑官方 quickstart：LCEL、Chat model、Prompt、Output parser | 一個 `hello_langchain.py` |
| 2 | **LangChain Retrieval** | 跑官方 RAG tutorial（用 Chroma + OpenAI/Ollama）| 一個能跑的 RAG notebook |
| 3 | **LangChain Agent + Tools** | 跑 ReAct agent、自定義 2 個 tool | `agent_demo.py` |
| 4 | **準備硬體語料** | 抓 OpenTitan docs / Verilog LRM PDF / RISC-V spec 整理進 `data/` | 結構化的文件目錄 |
| 5 | **Killer Project 起頭** | 建 repo、寫 README 骨架、設 pyproject、Docker skeleton | GitHub repo 開好 |
| 6 | **RAG pipeline v1** | chunking + embedding + Chroma + retrieve | `rag/` module |
| 7 | **休息 / 補課** | 週日：補 1–6 天沒做完的 + 整理筆記 | — |

### 🟡 Week 2：做出 Killer Project 主體

| Day | 主題 | 任務 | 產出 |
|---|---|---|---|
| 8 | **FastAPI 包 RAG** | `/ask` endpoint + streaming response | curl 可打 |
| 9 | **Eval set v1** | 寫 15–20 題 golden Q&A（硬體題目）| `eval/golden.jsonl` |
| 10 | **Eval pipeline** | retrieval recall@k + LLM-as-judge faithfulness | `eval/run.py` + 報表 |
| 11 | **Agent + tools** | LangChain Agent + tools（grep RTL / lookup spec / lint runner mock） | `/agent` endpoint |
| 12 | **Logging / Tracing** | 接 LangSmith free tier 或自寫 structured log | trace 截圖能秀 |
| 13 | **Claude Code-style Skill** | 寫一個 `skills/rtl_lint_fix/SKILL.md` + 對應 prompt template | 對齊 JD「reusable skills」 |
| 14 | **Docker + 部署** | docker-compose up 一鍵起服務，README 寫清楚 | 任何人 clone 都能跑 |

### 🔴 Week 3：講故事 + 模擬面試

| Day | 主題 | 任務 | 產出 |
|---|---|---|---|
| 15 | **改寫履歷 Fitipower 段** | 用 AI App 語言重寫，補 framework / interface / eval | 新版 resume |
| 16 | **錄 Demo 影片** | Loom 2–3 分鐘，講架構 + 跑一次給看 | YouTube unlisted / Loom link |
| 17 | **9 題技術 QA 寫稿** | 我給範本，你改成自己語氣，每題 30s + 2min 兩版 | `interview_qa.md` |
| 18 | **5 個 STAR 故事** | Ship / 跨團隊 / 失敗 / 學習 / Why NVIDIA | `interview_stories.md` |
| 19 | **模擬面試 Round 1** | 你對著鏡頭講，錄影回放 | 改進清單 |
| 20 | **模擬面試 Round 2** | 改完再錄一次 | OK 為止 |
| 21 | **緩衝 / 補洞** | 看哪邊還弱補哪邊 | — |

---

## Killer Project 主題

> **「SOC Design Doc Q&A + RTL Lint Fix Agent」**
>
> 一個 FastAPI 服務，包含：
> - **RAG**：可問 Verilog LRM / open-source SOC（如 OpenTitan / Ibex）文件
> - **Agent**：給一段 RTL，自動跑 lint → 解讀錯誤 → 建議修正
> - **Eval**：golden Q&A + LLM-as-judge

**為什麼這題**：硬體題材 + 涵蓋 JD 三大支柱（Service + RAG + Agent）+ 你能講硬體細節，**完全打到 NVIDIA SOC team 的點**。

---

## 立即今天可以開始的 3 件事

### 1. 開 GitHub repo（10 分鐘）
名字建議：`soc-design-ai-copilot` 或 `rtl-rag-agent`
**重要**：這個 repo 的 link 之後會放在你給 NVIDIA 的補充資料裡。

### 2. 環境準備（30 分鐘）
```bash
python -m venv .venv
pip install langchain langchain-community langchain-openai chromadb fastapi uvicorn pydantic
```
（之後可加 `langchain-ollama` 跑本地模型省成本）

### 3. 先跑一次官方 LangChain Quickstart（1.5 hr）
網址：https://python.langchain.com/docs/tutorials/rag/
**目標**：今天結束時，你能跑一個「丟一個 PDF → 問問題 → 得到答案」的 script。

剩下的 1 hr：把跑通的東西**寫一份 5 行筆記**——「我學到 LangChain 的 LCEL 是怎麼接的、Retriever interface 長怎樣」。

---

## 接下來會產出的子文件（在 `plan/` 資料夾內）

1. **`Project_Spec.md`** — Killer Project 的完整技術規格（檔案結構、API schema、eval 方法、Dockerfile）
2. **`Week1_Daily_Tasks.md`** — Week 1 七天每天 3hr 的逐步任務清單（含 code snippet 和檢核點）
3. **`Fitipower_Story_Template.md`** — Fitipower 經驗 STAR 重寫模板（填空式）
4. **`Interview_QA_Bank.md`** — 9 題技術問答的範本答案

---

## 一句話總結策略

> 不要用「讀書」準備，要用「**做出一個能放 GitHub link 給面試官看的東西**」準備。
> 手上有 demo + 故事，被問到時你是在「介紹自己做的東西」而不是「回答考題」，立場完全不同。
