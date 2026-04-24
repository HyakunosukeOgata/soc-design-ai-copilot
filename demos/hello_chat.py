"""
hello_chat.py — 純 chat（沒有 agent、沒有 tool）

學習目標：
1. 理解 prompt | llm | parser 這個 LCEL pipe 在做什麼
2. 體會「invoke / stream / batch」三種呼叫方式
3. 對比 agent 版本，理解何時不該用 agent
"""
from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# === 1. 三個零件 ===
llm = init_chat_model("openai:gpt-4o-mini")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a SOC design assistant. Answer concisely in 3 bullet points."),
    ("user", "Explain {concept} to a junior hardware engineer."),
])

parser = StrOutputParser()


# === 2. 用 LCEL pipe 串起來 ===
chain = prompt | llm | parser
#         ^      ^     ^
#         |      |     └─ 把 LLM 的 AIMessage 物件 → 純字串
#         |      └─ 把 prompt 結果送給 LLM 推理
#         └─ 把 {concept} 變數填進 template


# === 3. invoke：一次拿完整答案 ===
print("=" * 50)
print("【invoke 模式】等全部生成完才回")
print("=" * 50)
result = chain.invoke({"concept": "clock domain crossing"})
print(result)


# === 4. stream：邊生成邊回（user perceive latency 大幅下降）===
print("\n" + "=" * 50)
print("【stream 模式】token 一個個吐")
print("=" * 50)
for chunk in chain.stream({"concept": "metastability"}):
    print(chunk, end="", flush=True)
print()


# === 5. batch：同時跑多個 input（並行）===
print("\n" + "=" * 50)
print("【batch 模式】一次跑多題")
print("=" * 50)
results = chain.batch([
    {"concept": "setup time"},
    {"concept": "hold time"},
])
for i, r in enumerate(results):
    print(f"\n--- Result {i+1} ---")
    print(r)
