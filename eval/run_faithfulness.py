"""
Day 4 Hr 2: Faithfulness Eval (LLM-as-Judge)

評估兩件事：
1. Faithfulness: RAG 生成的答案是否有 retrieved context 支持？(0/1)
2. Refusal Accuracy: 對於 should_refuse 的問題，是否正確拒答？(0/1)

Pipeline:
  golden Q -> retriever -> context -> LLM 答 -> Judge LLM 評分 -> 統計
"""
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from src.rag import config
from src.rag.retriever import get_retriever

load_dotenv()

ROOT = config.ROOT
GOLDEN = ROOT / "eval" / "golden.jsonl"
REPORT = ROOT / "eval" / "reports" / "faithfulness_report.md"

# ---------- Build retriever (semantic — Hr 1 proved it best) ----------
retriever = get_retriever("semantic", top_k=3)

# ---------- RAG answer chain ----------
llm = ChatOpenAI(model=config.LLM_MODEL, temperature=0)

answer_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an SoC design assistant. Answer the user's question STRICTLY based on the provided context.\n"
     "If the context does not contain the answer, reply exactly: I don't know based on the provided documents."),
    ("user", "Context:\n{context}\n\nQuestion: {question}")
])
answer_chain = answer_prompt | llm | StrOutputParser()

# ---------- Judge chain ----------
judge_llm = ChatOpenAI(model=config.LLM_MODEL, temperature=0)
judge_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a strict evaluator. Given a CONTEXT and an ANSWER, decide if the ANSWER is fully "
     "supported by the CONTEXT (no hallucinations, no facts beyond the context).\n"
     "Return ONLY a JSON object: {{\"faithful\": true|false, \"reason\": \"short reason\"}}"),
    ("user", "CONTEXT:\n{context}\n\nANSWER:\n{answer}")
])
judge_chain = judge_prompt | judge_llm | JsonOutputParser()

# ---------- Helpers ----------
REFUSAL_MARKERS = ["i don't know", "i do not know", "cannot answer", "not in the provided"]

def is_refusal(text: str) -> bool:
    t = text.lower()
    return any(m in t for m in REFUSAL_MARKERS)

def load_golden():
    with open(GOLDEN, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]

# ---------- Run eval ----------
def main():
    golden = load_golden()
    rows = []
    faithful_total, faithful_pass = 0, 0
    refusal_total, refusal_pass = 0, 0

    for q in golden:
        qid = q["id"]
        question = q["question"]
        should_refuse = q.get("should_refuse", False)

        retrieved = retriever.invoke(question)
        context = "\n\n".join(d.page_content for d in retrieved)
        answer = answer_chain.invoke({"context": context, "question": question}).strip()
        refused = is_refusal(answer)

        if should_refuse:
            # Refusal test: 應該拒答
            refusal_total += 1
            ok = refused
            if ok:
                refusal_pass += 1
            rows.append({
                "id": qid, "type": "refusal",
                "question": question, "answer": answer,
                "expected": "REFUSE", "result": "PASS" if ok else "FAIL",
                "judge": "-"
            })
        else:
            # Faithfulness test: 應該答得有依據
            faithful_total += 1
            if refused:
                # 答不出來就視為 unfaithful（漏答也算 fail）
                rows.append({
                    "id": qid, "type": "faithful",
                    "question": question, "answer": answer,
                    "expected": "answer with grounding",
                    "result": "FAIL (refused)", "judge": "-"
                })
                continue
            try:
                verdict = judge_chain.invoke({"context": context, "answer": answer})
                faithful = bool(verdict.get("faithful", False))
                reason = verdict.get("reason", "")[:80]
            except Exception as e:
                faithful = False
                reason = f"judge_error: {e}"
            if faithful:
                faithful_pass += 1
            rows.append({
                "id": qid, "type": "faithful",
                "question": question, "answer": answer[:120],
                "expected": "answer with grounding",
                "result": "PASS" if faithful else "FAIL",
                "judge": reason
            })

    faith_rate = faithful_pass / faithful_total if faithful_total else 0
    refuse_rate = refusal_pass / refusal_total if refusal_total else 0

    # ---------- Print ----------
    print("\n=== Faithfulness Eval ===")
    print(f"Faithfulness: {faithful_pass}/{faithful_total} = {faith_rate:.2%}")
    print(f"Refusal Acc : {refusal_pass}/{refusal_total} = {refuse_rate:.2%}\n")
    print(f"{'ID':<5}{'TYPE':<10}{'RESULT':<18}QUESTION")
    print("-" * 90)
    for r in rows:
        print(f"{r['id']:<5}{r['type']:<10}{r['result']:<18}{r['question'][:55]}")

    # ---------- Report ----------
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("# Faithfulness Eval Report\n\n")
        f.write(f"- Faithfulness: **{faithful_pass}/{faithful_total} = {faith_rate:.2%}**\n")
        f.write(f"- Refusal Accuracy: **{refusal_pass}/{refusal_total} = {refuse_rate:.2%}**\n\n")
        f.write("## Per-Question Detail\n\n")
        f.write("| ID | Type | Result | Question | Answer (truncated) | Judge |\n")
        f.write("|----|------|--------|----------|--------------------|-------|\n")
        for r in rows:
            q = r["question"].replace("|", "\\|")
            a = r["answer"].replace("|", "\\|").replace("\n", " ")
            j = str(r["judge"]).replace("|", "\\|")
            f.write(f"| {r['id']} | {r['type']} | {r['result']} | {q} | {a} | {j} |\n")
    print(f"\nReport saved -> {REPORT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
