# 你的經歷 vs JD 落差分析

## 一、Match 度總評：**約 55–65%**

你是「**偏硬體側的 AI 工程師**」，而 JD 要的是「**偏 AI 應用 / 服務側、能聽懂硬體的工程師**」。方向相鄰但**重心相反**——這既是優勢也是風險。

---

## 二、強項（要在面試大力放大）

| JD 要的 | 你有的證據 | 怎麼包裝 |
|---|---|---|
| **硬體 sense（Stand Out 加分項）** | RTL、Verilog、FPGA/ASIC、Stratus HLS、Vivado、Xcelium、PPA、PD 概念 | 你是**真的懂硬體流程的 AI 工程師**，這在 NVIDIA SOC team 裡是稀缺人才——大多 AI 應用工程師完全聽不懂 user 在講什麼 |
| **LLM 應用於 EDA 自動化** | "LLM-Driven EDA Workflow Automation"、prompts + scripts 接 GPT、產生 design suggestions/debug insights、PPA +15% | **這項與 JD 的 "workflow automation for SOC Design tasks" 幾乎 1:1 對應**，是你的王牌，必須擴寫細節 |
| **跨團隊協作** | 與 compiler/software 團隊 co-design | 對應 JD 的 "co-work with Methodology, CAD, Design teams" |
| **Python / C++** | 有 | OK |
| **學歷** | NTU MS（CS/EE 背景符合）| 滿足 MS/PhD 要求 |
| **3+ 年經驗** | 2022/8 至今，~3.5 年 | 落在 1–5 年區間 |

---

## 三、明顯落差（**面試會被挑戰、需補強或話術轉化**）

### 🔴 高風險落差

| JD 要求 | 你的履歷現狀 | 嚴重度 |
|---|---|---|
| **Shipping production AI services（API、async、streaming）** | 履歷沒有 FastAPI、REST/gRPC、Docker、K8s、雲端/on-prem 部署字眼 | ⚠️⚠️⚠️ 致命 |
| **RAG（chunking / embedding / vector DB / rerank / eval）** | 完全沒提到 | ⚠️⚠️⚠️ 致命 |
| **LangChain 或同類 agent 框架** | 完全沒提到（你寫的是 prompt + script，比較像 light wrapper） | ⚠️⚠️ 高 |
| **Coding agent / IDE workflow（Claude Code、Cursor、reusable skills）** | 完全沒提到 | ⚠️⚠️ 高 |
| **Eval / logging / tracing / regression test for prompts** | 沒提到 | ⚠️⚠️ 高 |

### 🟡 中等落差
- **Web/Full-stack（React、TypeScript、FastAPI 前端）**：Nice-to-have，沒有也 OK，但若有能加分
- **軟體工程習慣**：dependency management、testing、interface design——履歷沒明寫，講得出來就好

---

## 四、面試風險預測（HR / Hiring Manager 會問）

> 「你的 LLM-Driven EDA Workflow 具體是什麼架構？是用 LangChain 嗎？怎麼評估 LLM 輸出品質？是 production service 還是 internal script？有 user？流量？」

→ **這題答不好直接出局**。你要把 Fitipower 那段「prompts + scripts 接 GPT」**重新解構成 AI Application 的語言**：
- 是不是有 input/output interface？是 CLI 還是 API？
- LLM call 怎麼管理？（重試、cost、latency）
- Prompt 怎麼版本控制？
- 怎麼驗證 LLM 給的 design suggestion 是對的？（這就是 evaluation）

---

## 五、立即補強建議（按 ROI 排序）

### 🥇 第一優先（兩週內可做完，**面試前必做**）
1. **做一個 RAG demo 並放 GitHub**：用 LangChain or LlamaIndex + 一個開源 vector DB（Chroma/Qdrant）+ 一份硬體相關文件（如 RISC-V spec、Verilog LRM、open-source SOC repo README），做一個 Q&A bot
   - **講故事**：「我用自己懂的硬體領域文件做 RAG，順便驗證 chunking 對技術文件的影響」
2. **把它包成 FastAPI service + Docker**：補齊「ship service」的證據
3. **加一個 eval script**：10–20 題 golden Q&A，跑 retrieval recall@k 與 LLM-as-judge faithfulness

### 🥈 第二優先（一週內）
4. **做一個 Agent demo**：LangChain Agent + 2–3 個 tool（例如：跑 Makefile、grep RTL、查 register spec），展示 multi-step plan
5. **寫一個 reusable "skill" 範例**：模仿 Claude Code skill 結構（SKILL.md + 程式），例如「RTL lint failure 自動分類與修復建議」skill

### 🥉 第三優先（履歷修改）
6. **改寫 Fitipower 那段**，補上：
   - 用了什麼 framework / library
   - 服務形式（CLI? API? Plugin?）
   - 多少 user 在用 / 跑了多少次
   - 怎麼 evaluate LLM 輸出
7. **新增一個 "Side Project / Open Source" section** 放上面那兩個 demo

---

## 六、結論與策略

### 你的差異化定位（面試開場一定要講）
> **「我不是純 AI 應用工程師，我是『真的看得懂 RTL 與 chip build flow』的 AI 工程師。我在前公司已經把 LLM 接進 EDA flow 拿到 PPA +15%，現在想把這個能力升級到 service / agent / RAG 等級，這正是這個職缺要的事。」**

### 競爭優勢
- 多數投這個缺的人**懂 LangChain 但聽不懂 RTL**
- 你**反過來**——而 NVIDIA SOC team 寧可教你 LangChain，也不想教 candidate Verilog

### 致命風險
- 若你被問 RAG / Agent / Production service 細節答不出來，**Hiring Manager 會懷疑你只是「寫 prompt 套 GPT」而不是 AI Application Engineer**

### 建議 Action
**面試前至少要有 1 個能 demo 的 RAG + 1 個 Agent project**，並把 Fitipower 經驗用 AI App 的語言重新講一次。
