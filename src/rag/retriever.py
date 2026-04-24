"""Retriever factory: semantic / bm25 / hybrid / hybrid+rerank."""
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import FlashrankRerank

from . import config
from .ingest import load_documents, split_documents, build_vectorstore


def build_retrievers(top_k: int = config.TOP_K):
    """Return dict {name: retriever} for all 4 strategies."""
    docs = load_documents()
    chunks = split_documents(docs)
    vs = build_vectorstore(chunks)

    semantic = vs.as_retriever(search_kwargs={"k": top_k})

    bm25 = BM25Retriever.from_documents(chunks)
    bm25.k = top_k

    hybrid = EnsembleRetriever(retrievers=[semantic, bm25], weights=[0.5, 0.5])

    reranker = FlashrankRerank(top_n=top_k)
    hybrid_rerank = ContextualCompressionRetriever(
        base_compressor=reranker, base_retriever=hybrid
    )

    return {
        "semantic": semantic,
        "bm25": bm25,
        "hybrid": hybrid,
        "hybrid_rerank": hybrid_rerank,
    }


def get_retriever(name: str = "semantic", top_k: int = config.TOP_K):
    return build_retrievers(top_k)[name]
