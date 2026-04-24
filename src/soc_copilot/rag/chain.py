"""LCEL chain: question -> retriever -> grounded answer or refusal."""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from soc_copilot.config import LLM_MODEL

REFUSAL_TEXT = "I don't know based on the provided documents."

_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an SoC design assistant. Answer the user's question STRICTLY based on the provided context.\n"
     f"If the context does not contain the answer, reply exactly: {REFUSAL_TEXT}"),
    ("user", "Context:\n{context}\n\nQuestion: {question}"),
])


def _format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)


def make_rag_chain(retriever, model: str = LLM_MODEL, temperature: float = 0):
    """Build an LCEL RAG chain returning a string answer."""
    llm = ChatOpenAI(model=model, temperature=temperature)
    return (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | _PROMPT | llm | StrOutputParser()
    )
