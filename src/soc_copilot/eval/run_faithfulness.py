"""Faithfulness eval: LLM-as-judge + refusal accuracy.

Run:
    python -m soc_copilot.eval.run_faithfulness
"""
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from soc_copilot.config import GOLDEN_PATH, REPORTS_DIR, JUDGE_MODEL
from soc_copilot.rag import build_index, make_retriever, make_rag_chain

REFUSAL_MARKERS = ["i don't know", "i do not know", "cannot answer", "not in the provided"]


def is_refusal(text: str) -> bool:
    t = text.lower()
    return any(m in t for m in REFUSAL_MARKERS)


def build_judge():
    judge_llm = ChatOpenAI(model=JUDGE_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a strict evaluator. Given a CONTEXT and an ANSWER, decide if the ANSWER is fully "
         "supported by the CONTEXT (no hallucinations, no facts beyond the context).\n"
         "Return ONLY JSON: {{\"faithful\": true|false, \"reason\": \"short reason\"}}"),
        ("user", "CONTEXT:\n{context}\n\nANSWER:\n{answer}"),
    ])
    return prompt | judge_llm | JsonOutputParser()


def main():
    golden = [json.loads(l) for l in GOLDEN_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    chunks, vs = build_index()
    retriever = make_retriever("semantic", vs, chunks, k=3)  # winner from Hr1
    rag = make_rag_chain(retriever)
    judge = build_judge()

    rows = []
    faith_total = faith_pass = 0
    refuse_total = refuse_pass = 0

    for q in golden:
        qid, question = q["id"], q["question"]
        should_refuse = q.get("should_refuse", False)

        retrieved = retriever.invoke(question)
        context = "\n\n".join(d.page_content for d in retrieved)
        answer = rag.invoke(question).strip()
        refused = is_refusal(answer)

        if should_refuse:
            refuse_total += 1
            ok = refused
            if ok:
                refuse_pass += 1
            rows.append({
                "id": qid, "type": "refusal",
                "question": question, "answer": answer,
                "result": "PASS" if ok else "FAIL", "judge": "-",
            })
        else:
            faith_total += 1
            if refused:
                rows.append({
                    "id": qid, "type": "faithful",
                    "question": question, "answer": answer,
                    "result": "FAIL (refused)", "judge": "-",
                })
                continue
            try:
                v = judge.invoke({"context": context, "answer": answer})
                faithful = bool(v.get("faithful", False))
                reason = (v.get("reason") or "")[:80]
            except Exception as e:
                faithful, reason = False, f"judge_error: {e}"
            if faithful:
                faith_pass += 1
            rows.append({
                "id": qid, "type": "faithful",
                "question": question, "answer": answer[:120],
                "result": "PASS" if faithful else "FAIL", "judge": reason,
            })

    fr = faith_pass / faith_total if faith_total else 0
    rr = refuse_pass / refuse_total if refuse_total else 0

    print("\n=== Faithfulness Eval ===")
    print(f"Faithfulness: {faith_pass}/{faith_total} = {fr:.2%}")
    print(f"Refusal Acc : {refuse_pass}/{refuse_total} = {rr:.2%}\n")
    print(f"{'ID':<5}{'TYPE':<10}{'RESULT':<18}QUESTION")
    print("-" * 90)
    for r in rows:
        print(f"{r['id']:<5}{r['type']:<10}{r['result']:<18}{r['question'][:55]}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = REPORTS_DIR / "faithfulness_report.md"
    with report.open("w", encoding="utf-8") as f:
        f.write("# Faithfulness Eval Report\n\n")
        f.write(f"- Faithfulness: **{faith_pass}/{faith_total} = {fr:.2%}**\n")
        f.write(f"- Refusal Accuracy: **{refuse_pass}/{refuse_total} = {rr:.2%}**\n\n")
        f.write("## Per-Question Detail\n\n")
        f.write("| ID | Type | Result | Question | Answer (truncated) | Judge |\n")
        f.write("|----|------|--------|----------|--------------------|-------|\n")
        for r in rows:
            q = r["question"].replace("|", "\\|")
            a = r["answer"].replace("|", "\\|").replace("\n", " ")
            j = str(r["judge"]).replace("|", "\\|")
            f.write(f"| {r['id']} | {r['type']} | {r['result']} | {q} | {a} | {j} |\n")
    print(f"\nReport saved -> {report.relative_to(REPORTS_DIR.parent.parent)}")


if __name__ == "__main__":
    main()
