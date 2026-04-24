"""Retriever factory: one entry-point for all 4 retrieval strategies.

Usage:
    chunks, vs = build_index()
    retriever = make_retriever("hybrid_rerank", vs, chunks)
    docs = retriever.invoke("query")
"""
from typing import Literal
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import (
    EnsembleRetriever, ContextualCompressionRetriever,
)
from langchain_community.document_compressors import FlashrankRerank
from flashrank import Ranker

from soc_copilot.config import DEFAULT_K, RERANK_POOL_K, RERANKER_MODEL

RetrieverKind = Literal["semantic", "bm25", "hybrid", "hybrid_rerank"]


def make_retriever(
    kind: RetrieverKind,
    vectorstore,
    chunks,
    k: int = DEFAULT_K,
):
    """Build one of the 4 retriever variants.

    Args:
        kind: "semantic" | "bm25" | "hybrid" | "hybrid_rerank"
        vectorstore: Chroma instance from build_index()
        chunks: list of Documents from build_index()
        k: top-k results to return
    """
    if kind == "semantic":
        return vectorstore.as_retriever(search_kwargs={"k": k})

    if kind == "bm25":
        bm25 = BM25Retriever.from_documents(chunks)
        bm25.k = k
        return bm25

    if kind == "hybrid":
        sem = vectorstore.as_retriever(search_kwargs={"k": k})
        bm25 = BM25Retriever.from_documents(chunks)
        bm25.k = k
        return EnsembleRetriever(retrievers=[sem, bm25], weights=[0.5, 0.5])

    if kind == "hybrid_rerank":
        sem = vectorstore.as_retriever(search_kwargs={"k": RERANK_POOL_K})
        bm25 = BM25Retriever.from_documents(chunks)
        bm25.k = RERANK_POOL_K
        pool = EnsembleRetriever(retrievers=[sem, bm25], weights=[0.5, 0.5])
        ranker = Ranker(model_name=RERANKER_MODEL)
        compressor = FlashrankRerank(client=ranker, top_n=k, model=RERANKER_MODEL)
        return ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=pool,
        )

    raise ValueError(f"Unknown retriever kind: {kind}")
