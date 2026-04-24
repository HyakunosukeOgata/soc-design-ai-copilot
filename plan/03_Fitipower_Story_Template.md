# Fitipower 經驗 STAR 重寫模板

## 為什麼需要這份
你履歷上的 Fitipower 經驗寫得太「硬體 / 結果」導向，但 NVIDIA 這個職缺要看的是**AI Application Engineer 的能力證據**。

同一段經歷，**重新用 AI App 的語言講一次**，立刻就能對齊 JD。

---

## STAR 結構說明

- **S (Situation)**：當時的背景與挑戰
- **T (Task)**：你被指派 / 主動接下的具體任務
- **A (Action)**：你做了什麼（**80% 的時間花在這裡**）
- **R (Result)**：產出與量化指標

---

## 故事 1：LLM-Driven EDA Workflow Automation（旗艦故事，必背）

### 30 秒電梯版（填空）
> 「我在 Fitipower 主導開發了一套 **__________**（服務形式：CLI / API / IDE plugin），把 LLM 整合進 EDA flow 來自動化 **__________**（哪個環節：parameter tuning / log 分析 / debug suggestion）。我設計了 **__________**（技術做法：domain-specific prompts + script orchestration）的架構，最後在 **__________**（哪類 design）上拿到 **PPA 提升 15%**，並且讓工程師的迭代次數從 **__________** 降到 **__________**。」

### 2–3 分鐘深度版

#### S (Situation)
> 填空：當時 EDA flow 中的 ___________ 環節需要工程師反覆手動嘗試 ___________ 個參數組合，每次跑 flow 要 ___________ 小時，整個 design close 平均要 ___________ 週。團隊希望用 AI 降低這個迭代成本。

**範例**：
> 「在 Fitipower，我們的 SOC design flow 中『synthesis 參數調校』這個環節高度依賴資深工程師的經驗。每次調 timing / area trade-off 時，工程師要手動嘗試 10–20 組參數組合，每跑一次 flow 要 6–8 小時，整個 design close 通常需要 3–4 週。團隊希望導入 LLM 來輔助這個決策過程。」

#### T (Task)
> 我被指派 / 主動提案，要設計一個 **____________**（服務 / 工具）讓工程師可以：
> 1. ____________ （輸入什麼）
> 2. 系統自動 ____________ （做什麼處理）
> 3. 輸出 ____________ （什麼結果）

#### A (Action) ← **80% 時間花在這**

**用 AI App 的語言講，分 4 個面向：**

##### A1. 系統設計
- 服務形式：是 CLI、Python script、還是接成 plugin？
- Input / output schema 怎麼設計？
- 怎麼跟現有 EDA flow 整合？（command line wrapper？檔案 watch？）

**填空**：
> 「我把這個工具做成 ____________（形式），暴露 ____________（介面），讓使用者用 ____________ 方式呼叫。Input 是 ____________，Output 是 ____________。」

##### A2. LLM 整合與 prompt 設計
- 用了哪個模型？（GPT-4 / GPT-3.5 / 內部 model？）
- Prompt 怎麼版本管理？（如果只是寫死在 code 裡，誠實講，但補一句「我學到這是個問題，現在的 best practice 是 ___」）
- 怎麼把 domain knowledge（EDA flow 的領域知識）放進 prompt？是 system prompt、few-shot example、還是 retrieval？

**填空**：
> 「我用了 ____________ 模型，prompt 設計上我用 ____________（system prompt 描述 EDA flow 角色 + few-shot 給 N 個範例）。為了讓 LLM 理解我們特定的 design library，我把 ____________（哪些 reference data）以 ____________ 方式注入 context。」

##### A3. Tool / 自動化串接
- LLM 輸出的建議怎麼變成實際的 EDA action？
- 有沒有迭代式（LLM 建議 → 跑 flow → 看結果 → 再問 LLM）？這就是 agent loop！

**填空**（**這段超重要，幫你升級成「我做的就是 agent」**）：
> 「我把整個流程設計成一個 close-loop：LLM 給出參數建議 → 我寫的 wrapper script 自動更新 flow config → 跑 EDA tool → parse 出 PPA 結果 → 把結果再 feed 回 LLM 做下一輪建議。這其實就是一個 multi-step agent 架構，只是當時我沒用 LangChain，是手寫的 orchestration。」
>
> 接著補一句**展現你會反思**：
> 「現在回頭看，如果當時用 LangChain 的 AgentExecutor，可以省掉很多 retry / state management 的手刻邏輯，這也是我目前在補強的方向。」

##### A4. 評估與品質控制
- LLM 的建議是不是真的有效？怎麼驗證？
- 有沒有 fallback / safety check？

**填空**（**這段對應 JD 的 evaluation 要求**）：
> 「為了驗證 LLM 給的建議真的可靠，我建立了 ____________（多少組）baseline test cases，每次 prompt 改版我都重跑一次比較 PPA delta。如果新 prompt 在 baseline 上 regression，我就回滾。」
>
> 如果你當時沒做 eval，誠實但有 framing：
> 「當時我們是用人工 review LLM 建議再決定是否採用——這是個 weakness，現在我會用 LLM-as-judge + golden test set 自動化這件事。」

#### R (Result)
- **PPA 提升 15%**（你已有）
- **量化使用者影響**：幾個 designer 在用？跑了幾次？省下多少 engineer-hour？
- **其他 secondary metric**：iteration 次數降低？convergence 時間縮短？

**填空**：
> 「最終，這套工具在 ____________（幾個 project）上線，____________（幾位）designer 在用，total ____________ 次呼叫。在目標 design 上 PPA 改善 15%、iteration 次數從平均 ____________ 降到 ____________、design close 時間從 ____________ 週縮短到 ____________ 週。」

---

## 故事 2：跨團隊協作（對應 JD 的 "Co-work with Methodology, CAD, Design"）

### 30 秒版
> 「我在 Fitipower 跟 compiler 和 software 團隊合作做 AI accelerator 整合，要把我們做的 custom operator 串進他們的 inference pipeline。我負責 ____________，過程中我學到 ____________（跨領域溝通的點）。」

### 2 分鐘版（STAR）

**S**：accelerator 端（你）和 compiler 端要對齊 op spec / API contract，但兩邊術語完全不同。

**T**：你要主導定出一份共同的 interface spec。

**A**：
- 主動約 weekly sync
- 寫了一份「給 compiler team 看的硬體 op spec 文件」（**用對方聽得懂的話翻譯**）
- 用範例 + 視覺化降低溝通成本

**R**：
- 100% functional coverage 達成
- end-to-end latency overhead 控制在 ____________ 以下

**面試 tie-in**：
> 「這段經驗讓我學會跟非自己領域的工程師合作。NVIDIA 這個職缺要跟 Methodology / CAD / Design 三個團隊合作，我覺得我已經有這個跨領域翻譯的肌肉。」

---

## 故事 3：失敗 / 學到教訓（一定會被問）

選一個**真的失敗過、有反思、沒有讓公司大爆炸**的故事。

### 推薦選材方向
- 某個 LLM prompt 在 dev 跑得很好但實際用會 hallucinate
- 某次 agent 邏輯讓 EDA tool 跑了不該跑的東西
- 某次 estimate 錯時程
- 某個技術決策（例如選某個 framework）後來證明錯誤

### 模板
> **S**：當時 ____________
> **T**：我以為 ____________
> **A**：但實際上 ____________ 出問題，我做了 ____________ 補救
> **R**：最後 ____________，**我學到的是 ____________**（這句最重要）

**反面教材**（不要講）：
- 「我犯的錯是太追求完美」← 假
- 「我跟同事吵架」← 紅旗
- 公司機密 / 怪罪別人

---

## 故事 4：主動學習（你有素材：MIT Han Lab、200 LeetCode）

### 模板
> 「我會固定追 ____________（MIT Han Lab、Anthropic blog、LangChain release notes...）。最近讓我印象深刻的是 ____________（某篇論文 / 某個技術），我覺得它能應用到 ____________。」
>
> 「同時我有刷 200+ LeetCode，主要練 ____________（system design / 演算法），目的是 ____________（保持 problem solving 手感、面對大規模系統的思考）。」

---

## 故事 5：Why NVIDIA SOC Team（**100% 會被問，請務必背熟**）

### 結構：個人故事 → 為什麼是這團隊 → 為什麼是這時間點

#### 個人故事（30 秒）
> 「我從 NTU 念的是生醫電子，但碩論做 deep RL + ResNeSt 之後，我就確定我要做『AI 跟硬體的交集』。在 Fitipower 三年多，我做的就是把 AI 跑進 FPGA/ASIC，並且開始用 LLM 加速 EDA 流程。」

#### 為什麼是這團隊（30 秒）
> 「NVIDIA 這個職缺剛好是我這條軌跡的下一步：從『把 AI 跑進硬體』升級到『用 AI 加速整個 SOC design flow』。而且這個團隊的 user 是真的 SOC designer，我能聽懂他們的痛點，這是我跟其他 AI candidate 不一樣的地方。」

#### 為什麼是這時間點（30 秒）
> 「現在剛好是 LLM 從 chat 進化到 agent 的轉折點，Claude Code-style 的 reusable skill 模式正在重新定義 engineering workflow。NVIDIA 的 SOC team 在這個時間點導入 AI 服務，我想 in early。」

---

## 你接下來要做的事

### 今天（30 分鐘就能做完）
1. 印出 / 開啟這份檔案
2. 把**故事 1 的所有填空**先填一遍（用真實數字）
3. 對著鏡頭講一次故事 1 的 30 秒版，錄音聽聽看順不順

### 本週內
4. 5 個故事都完成填空
5. 對著鏡頭錄影練習，每個故事練 3 次

### 面試前一週
6. 找一個朋友 / ChatGPT 模擬面試，丟這 5 個故事的觸發問題給你

---

## 講故事的 3 大禁忌

1. ❌ **只講結果不講過程**：「我做了 X 拿到 15%」← 面試官會問你怎麼做的
2. ❌ **太多技術細節沒有 outcome**：講 30 分鐘但聽不出影響
3. ❌ **第一人稱含糊**：「我們做了...」← 要清楚講「**我**做了什麼」vs「team 做了什麼」

## 講故事的 3 大加分

1. ✅ **量化**：所有數字都要有
2. ✅ **反思**：講完現況後加一句「現在回頭看，我會 ___」
3. ✅ **連結 JD**：每個故事結尾接一句「這對應到 NVIDIA 這個職缺的 ___」
