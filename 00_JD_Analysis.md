# NVIDIA SOC Design — AI Engineer JD 分析

## 一、職缺定位

這個職缺是 **NVIDIA SOC (System-on-Chip) 硬體設計團隊內部的 AI 應用工程師**，不是做 AI 模型研究，也不是做晶片設計，而是 **「用 AI 工具加速硬體工程師工作流程」** 的橋樑角色。

簡單說：**你是服務 SOC Hardware Team 的 AI Application Engineer**。

---

## 二、核心工作三大支柱

| 支柱 | 內容 | 技術關鍵字 |
|---|---|---|
| **1. LLM Services** | API、async job、streaming、串內部工具/資料 | FastAPI、gRPC、Docker |
| **2. RAG / 知識系統** | chunking、embedding、vector DB、rerank、權限控管、延遲/品質調校 | LangChain、向量資料庫（Milvus/Qdrant/Weaviate）、reranker |
| **3. Agent & 自動化** | Tool use、multi-step plan、memory、guardrails，做成可重複使用的 "skills/playbooks" | LangChain Agent、Claude Code-style skills、IDE workflow |

加上 **Reliability / Eval**：logging、tracing、prompt regression test、usefulness & safety metrics。

---

## 三、JD 中的關鍵訊號（值得留意）

1. **"Claude Code-class assistants, reusable skills / playbooks"** 被提到兩次  
   → 團隊已經（或想要）走 Claude Code + Skills 的工作模式，**面試時務必能談你對 skill-based agent 架構的理解與實作經驗**。

2. **"Co-work with Methodology, CAD, and Design teams"**  
   → 你的 stakeholder 是硬體工程師（不是 PM、不是一般 SW user），**溝通力 + 願意理解 RTL/Build flow** 是錄取關鍵。

3. **"shipping and operating"** + **"online production-ready"**  
   → 不是 PoC / Notebook 工程師，必須能扛 production service（部署、監控、回歸測試）。

4. **"proprietary data"**  
   → 一切都在內網 / on-prem，要熟悉地端部署、權限控管、不能依賴 OpenAI public API 的場景。

---

## 四、Must-Have vs Nice-to-Have 對照

### 硬性要求（缺一就難過）
- MS/PhD（CS/CE/EE）
- 1–5 年 **AI 應用開發**（強調是 product，不是 script）
- Python + 服務化部署經驗（REST/gRPC、容器）
- LangChain（或同類）+ RAG 實戰
- 用過 coding agent（Claude Code、Cursor、Copilot Agent…）
- 軟體工程基本功：依賴管理、設定管理、測試、介面設計

### 加分項（Stand Out）
- **硬體 sense**：看得懂 RTL（Verilog/SystemVerilog）、Makefile、SOC flow、PD 概念  
  → 不需會設計晶片，但要能聽懂 user 在講什麼
- **Web/Full-stack**：React/TypeScript + FastAPI，能自己做 internal portal 給硬體工程師用

---

## 五、面試準備建議

### 一定要準備的故事（用 STAR 講）
1. **一個你 ship 到 production 的 LLM service**：流量、延遲、評估指標、踩過的坑
2. **一個 RAG 系統**：你怎麼選 chunking 策略、embedding model、retrieval / rerank、怎麼評估品質（recall@k、faithfulness）、怎麼處理權限
3. **一個 Agent / Workflow 自動化**：tool design、失敗處理、guardrail、為何不用 single-prompt 解決
4. **一個 reusable skill / playbook**：你怎麼把重複工作抽象成 agent 能執行的「程序」
5. **一次跨團隊合作**：跟非 AI 背景的人 scope 問題、迭代交付

### 技術深度題預期方向
- RAG 為什麼 retrieve 不到？怎麼 debug？（hybrid search、query rewriting、HyDE…）
- Prompt regression test 怎麼設計？金標資料怎麼維護？
- Agent 跑飛了怎麼辦？（cost guard、step limit、human-in-the-loop）
- 模型評估：LLM-as-judge 的問題與校正

### 加分準備（你若想拉開差距）
- **讀一些 SOC build flow 基本概念**：synthesis、PnR、DV、UVM、Lint、CDC 是在做什麼，Makefile 在 chip build 中扮演角色
- 準備 1 個小 demo：例如 「給我一份 RTL spec，agent 自動產出 testbench skeleton」 或 「Makefile Q&A bot over internal docs」

---

## 六、整體評估

這個缺非常「**現代 AI Application Engineer 的標配**」，而且公司是 NVIDIA、領域是 SOC——**user 含金量高、資料封閉、問題明確**，是很好的成長環境。

**最容易被淘汰的點**：只會做 PoC / 只會寫 prompt / 沒有 production 經驗。  
**最容易拿到 offer 的點**：你能展示「**從 scope → ship → 維運 → 評估**」完整迴圈，並且**對硬體領域有好奇心而非排斥**。
