# Week 1 每日任務清單（每天 3 hr）

## 總目標
週末結束時，你要：
- 對 LangChain 的 LCEL / Retriever / Agent 三大概念**手上跑過**
- Killer Project 的 repo 已開好，RAG pipeline v1 可 retrieve

---

## Day 1（一）：LangChain 速成 — LCEL & Chat Model

### 學習目標
理解 LangChain 的核心抽象：`Runnable`、`PromptTemplate`、`ChatModel`、`OutputParser`、LCEL pipe `|`。

### 任務拆解

**Hr 1 — 看官方 quickstart（45min）+ 讀 LCEL 概念（15min）**
- https://python.langchain.com/docs/tutorials/llm_chain/
- https://python.langchain.com/docs/concepts/lcel/

**Hr 2 — 動手寫 `hello_langchain.py`**
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a SOC design assistant."),
    ("user", "Explain {concept} in 3 bullet points."),
])
chain = prompt | llm | StrOutputParser()

print(chain.invoke({"concept": "clock domain crossing"}))
```
- 跑通
- 改成 streaming：`for chunk in chain.stream({...}): print(chunk, end="")`
- 改成 async：`await chain.ainvoke(...)`

**Hr 3 — 寫筆記 + 自我測驗**
建一份 `notes/day01_langchain_basics.md`，回答以下 5 題：
1. LCEL 的 `|` 在做什麼？背後的型別是什麼？
2. `invoke` / `stream` / `batch` / `ainvoke` 差別？
3. `ChatPromptTemplate` 跟 `PromptTemplate` 差別？
4. `StrOutputParser` 為什麼要存在？不加會怎樣？
5. 怎麼塞「歷史對話」進去？（先看一下，明天會用）

### 檢核
- [ ] `hello_langchain.py` 能跑出 streaming 輸出
- [ ] 筆記 5 題都能用自己的話回答

---

## Day 2（二）：LangChain Retrieval — RAG 第一次

### 學習目標
跑通一個完整的 RAG flow，理解 `DocumentLoader` → `TextSplitter` → `Embedding` → `VectorStore` → `Retriever`。

### 任務拆解

**Hr 1 — 讀官方 RAG tutorial**
- https://python.langchain.com/docs/tutorials/rag/

**Hr 2 — 動手做**
- 找一份 PDF（建議直接抓 RISC-V spec 第 1 章 PDF：https://riscv.org/specifications/）
- 寫 `rag_demo.ipynb`：
```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Load
docs = PyPDFLoader("riscv_spec.pdf").load()
# Split
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
chunks = splitter.split_documents(docs)
# Embed + store
vs = Chroma.from_documents(chunks, OpenAIEmbeddings(model="text-embedding-3-small"))
# Retrieve
retriever = vs.as_retriever(search_kwargs={"k": 5})
print(retriever.invoke("What is RV32I?"))
```

**Hr 3 — 接成完整 RAG chain**
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

prompt = ChatPromptTemplate.from_template("""
Answer based ONLY on the context. If not in context, say "I don't know".
Context: {context}
Question: {question}
""")

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)
print(rag_chain.invoke("What is the difference between RV32 and RV64?"))
```

### 檢核
- [ ] 能 retrieve 出相關段落
- [ ] RAG chain 給的答案能引用 PDF 內容
- [ ] 試問一題 PDF 沒有的問題（如「天氣如何？」）→ 會回 "I don't know"

---

## Day 3（三）：LangChain Agent + Tools

### 學習目標
理解 ReAct pattern、`@tool` decorator、`AgentExecutor`、tool calling。

### 任務拆解

**Hr 1 — 讀文件**
- https://python.langchain.com/docs/tutorials/agents/
- 重點看「Tool calling」與「ReAct」差別

**Hr 2 — 寫 `agent_demo.py`**
```python
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

@tool
def count_lines(text: str) -> int:
    """Count the number of lines in a text."""
    return len(text.splitlines())

@tool
def find_module_name(rtl: str) -> str:
    """Find the Verilog module name from RTL code."""
    import re
    m = re.search(r"module\s+(\w+)", rtl)
    return m.group(1) if m else "not found"

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), [count_lines, find_module_name])

result = agent.invoke({"messages": [("user", "How many lines and what's the module name? RTL:\nmodule foo;\n  wire a;\nendmodule")]})
for m in result["messages"]:
    print(m.type, ":", m.content)
```

**Hr 3 — 觀察 + 思考**
- 把 verbose 開到最大，看 agent 的 thought / action / observation
- 故意問一個會讓它失敗的問題，看會怎樣
- 寫 `notes/day03_agent.md`：
  1. ReAct 的 thought-action-observation loop 你看到幾輪？
  2. 如果不給 tool docstring 會怎樣？（試試看）
  3. 如果你問「現在幾點」（沒有對應 tool），它會怎麼回應？

### 檢核
- [ ] Agent 能正確選 tool 並回答
- [ ] 你能看懂 trace 的每一步
- [ ] 筆記 3 題能回答

---

## Day 4（四）：準備硬體語料

### 任務拆解

**Hr 1 — 蒐集**
建議下載（任選 2–3 份，不用全要）：
- IEEE 1800 SystemVerilog LRM（找公開摘要 PDF 或用 OpenTitan style guide 替代）
- OpenTitan docs：https://opentitan.org/book/  → clone repo 取 `doc/` 目錄
- Ibex Core docs：https://github.com/lowRISC/ibex/tree/master/doc
- RISC-V Unprivileged ISA Spec PDF

**Hr 2 — 整理結構**
```
data/
├── opentitan/
│   ├── *.md
│   └── _meta.json   # {"source": "opentitan", "version": "..."}
├── ibex/
│   └── *.md
└── riscv_spec/
    └── riscv-spec.pdf
```

**Hr 3 — 寫 `src/rag/ingest.py` 草稿**
- 能 walk 整個 `data/` 目錄
- 能根據副檔名（.md / .pdf）分流到對應 loader
- 把 source 路徑放進 metadata
- 先**只印出 chunks 數量**，不真的存

### 檢核
- [ ] `data/` 目錄整理好
- [ ] `python -m src.rag.ingest` 能列出「總共 N 個 chunks，分布如下...」

---

## Day 5（五）：Killer Project 起頭（建 repo）

### 任務拆解

**Hr 1 — 建 GitHub repo + 本地骨架**
```bash
# GitHub 上建 repo: soc-design-ai-copilot (public, MIT license)
git clone <repo>
cd soc-design-ai-copilot

# 建立目錄
mkdir -p src/{rag,agent,api,observability} skills/rtl_lint_fix eval/reports tests notebooks data
touch README.md pyproject.toml Dockerfile docker-compose.yml .env.example .gitignore
```

**Hr 2 — `pyproject.toml` + 環境**
```toml
[project]
name = "soc-design-ai-copilot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "langchain>=0.3",
    "langchain-openai",
    "langchain-community",
    "langchain-chroma",
    "langgraph",
    "fastapi",
    "uvicorn[standard]",
    "pydantic-settings",
    "pypdf",
    "rank-bm25",
    "sse-starlette",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio", "ruff", "ipykernel"]
```

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

**Hr 3 — README skeleton**
- 寫好 README 大綱（標題、placeholder 圖、quick start TBD）
- `git commit -m "chore: project skeleton"` 推上去

### 檢核
- [ ] GitHub repo 公開，README 看得到
- [ ] `pip install -e .` 成功
- [ ] 至少 1 個 commit

---

## Day 6（六）：RAG pipeline v1（接到專案內）

### 任務拆解

**Hr 1 — `src/rag/ingest.py` 完整版**
- 能把 Day 4 整理的 `data/` 真的存進 Chroma
- CLI: `python -m src.rag.ingest --rebuild`

**Hr 2 — `src/rag/retriever.py`**
- Wrap 一個 retriever class，有 `retrieve(query, k=5)` 方法
- 先做 semantic only，hybrid 留到 Week 2

**Hr 3 — `src/rag/chain.py` + smoke test**
- LCEL chain：question → retriever → prompt → llm → parser
- 在 `notebooks/smoke_test.ipynb` 跑 3 個硬體題目驗證

### 檢核
- [ ] `python -m src.rag.ingest` 能成功建 Chroma
- [ ] 在 notebook 問「What is OpenTitan?」會引用實際文件回答
- [ ] commit + push

---

## Day 7（日）：休息 / 補課 / 整理

### 選一條路走

**A 路：上週順利**
- 整理 `notes/week1_summary.md`
- 把 README 加上一張**目前的架構圖**（手畫拍照也行）
- 額外讀：LangChain Expression Language deep dive
- 早點睡

**B 路：上週有 1–2 天落後**
- 把缺的補完
- 不要在這週末 burnout

**C 路：上週進度順利且有餘力**
- 提早做 Week 2 Day 8（FastAPI 包 RAG）
- 但**不要連續工作**

### 週日反省（5 題）
寫進 `notes/week1_retro.md`：
1. 這週最卡的概念是什麼？
2. LCEL 你敢在面試講解了嗎？
3. RAG 你能畫出完整 pipeline 嗎？
4. Agent 的 thought-action-observation loop 你能背嗎？
5. 下週最擔心哪一天？

---

## Week 1 結束時的成果清單

- [ ] GitHub repo 公開可看
- [ ] `data/` 有 2–3 份硬體文件
- [ ] `src/rag/` 三個檔案能跑通
- [ ] 1 個 RAG smoke test notebook
- [ ] 1 個 agent demo（獨立 script）
- [ ] 至少 4 篇學習筆記在 `notes/`
- [ ] 至少 5 個 commit

**達成這個清單 = Week 2 才有東西可以蓋上去**。寧可少做不要跳過。
