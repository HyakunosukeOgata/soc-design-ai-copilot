"""End-to-end RAG chain: question -> retrieve -> answer (grounded)."""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from . import config
from .retriever import get_retriever


SYSTEM_PROMPT = (
    "You are an SoC design assistant. Answer the user's question STRICTLY based on the provided context.\n"
    "If the context does not contain the answer, reply exactly: "
    "I don't know based on the provided documents."
)


def _format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)


def build_rag_chain(retriever_name: str = "semantic"):
    retriever = get_retriever(retriever_name)
    llm = ChatOpenAI(model=config.LLM_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "Context:\n{context}\n\nQuestion: {question}"),
    ])
    return (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt | llm | StrOutputParser()
    )


def main():
    chain = build_rag_chain("semantic")
    for q in [
        "What is the read latency of the AXI4-Lite slave?",
        "Why use Gray-code in the CDC FIFO?",
        "What is the price of NVIDIA H100?",
    ]:
        print(f"\nQ: {q}\nA: {chain.invoke(q)}")


if __name__ == "__main__":
    main()
