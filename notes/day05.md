# Day 5 — 重構成 Production-Grade Package + GitHub 上線

## 今天做了什麼
把 4 個散裝實驗腳本重構成一個可安裝的 Python package，推上 GitHub。

**Repo**: https://github.com/HyakunosukeOgata/soc-design-ai-copilot

### 產出
- `pyproject.toml` — 可 `pip install -e .[dev]`，3 個 console scripts
- `src/soc_copilot/` package：
  - `config.py` — 集中所有路徑、model 名、chunk 參數
  - `rag/{ingest, retriever, chain}.py` — 核心模組（factory pattern）
  - `eval/{run_retrieval, run_faithfulness}.py` — 共用 rag 模組
  - `demos/{rag_demo, hybrid_demo}.py` — smoke tests
- `README.md` — 結果表格 + roadmap
- `.env.example` — 給 reviewer 看怎麼 setup

---

## 重構前 vs 重構後

| 維度 | Before | After |
|---|---|---|
| 程式組織 | 散裝 4 個 hello_*.py + 2 個 eval/ 腳本 | `soc_copilot` package |
| 重複程式碼 | 每個腳本自己 load/split/embed | 共享 `build_index()` |
| Retriever 切換 | 各腳本硬編碼 | `make_retriever(kind, vs, chunks)` factory |
| Config | 散在每個檔案 | `soc_copilot/config.py` 集中 |
| 安裝 | 沒有，要 `python script.py` | `pip install -e .` 後 `python -m soc_copilot.xxx` |
| 程式碼變化 | -792 行 / +526 行 | 淨減 266 行（純樣板移除）|

---

## 核心設計模式

### 1. Factory Pattern — `make_retriever`
```python
retriever = make_retriever("hybrid_rerank", vs, chunks, k=3)
```
4 種 retriever 用同一介面切換 → eval 腳本只需 1 個 for loop 跑 4 次。

### 2. LCEL Chain Builder — `make_rag_chain`
```python
chain = make_rag_chain(retriever, model="gpt-4o-mini", temperature=0)
chain.invoke("question")
```
Retriever 跟 chain 解耦 → 隨時換 retriever 不用改 chain。

### 3. Centralized Config
```python
# soc_copilot/config.py
LLM_MODEL = "gpt-4o-mini"
CHUNK_SIZE = 400
DEFAULT_K = 3
```
所有模組都 `from soc_copilot.config import ...` → 改一個地方全套生效。

---

## 採坑紀錄

### Bug 1: `parents[2].parent` 多算一層
- `Path(__file__).resolve().parents[2].parent` 跑到 repo 上層 → `D:\Code\Interview\data` 不存在
- 修：`parents[2]`（src/soc_copilot/config.py → 上 3 層 = repo root）

### Bug 2: git 沒設 user.name/email
- 第一次 commit fatal: `unable to auto-detect email address`
- 修：`git config user.name/email`

### Bug 3: `gh` CLI 沒登入
- 跳過，改用手動 GitHub web 建 repo + `git remote add` + `git push`

---

## 面試 Soundbites

> 「我把 4 個實驗腳本重構成 installable package。Retriever 從硬編碼變成 factory function，eval 跟 demo 共用同一份 ingest 邏輯 — 淨減 266 行樣板程式碼。」

> 「我把 model name、chunk size、path 全集中到 config.py。面試官問『如果想換 model 從 gpt-4o-mini 換到 Claude Sonnet 要改幾個地方？』答案是 1 個。」

> 「Factory pattern 讓 eval 腳本變得很簡潔 — 一個 for loop 跑 4 種 retriever，沒有 if-else 樹。新增第 5 種 retriever 只要在 factory 加一行。」

> 「`pip install -e .` + console scripts → 任何人 clone 完 5 行指令就能 reproduce 我的所有 eval 數字。Reproducibility 是 production AI 的基本要求。」

---

## Day 5 Done ✅
週末選項：
- A: 整理 week1_summary + 畫架構圖
- B: 補課
- C: 提早做 Day 8（FastAPI 包 RAG 成 service）

下週開始：FastAPI service + Docker + Agent layer。
