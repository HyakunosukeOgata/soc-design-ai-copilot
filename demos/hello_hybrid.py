"""
hello_hybrid.py — 比較三種 retriever：Semantic / BM25 / Hybrid

學習目標：
1. 親眼看到「同一個 query，三種 retriever 抓到不同 chunks」
2. 理解 hybrid 為什麼互補（semantic 抓語意 + BM25 抓關鍵字）
3. 知道 EnsembleRetriever 怎麼把兩邊融合（RRF）
"""
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_community.document_compressors import FlashrankRerank


# ============================================================
# 1. Load + Split — 跟之前一樣
# ============================================================
print("[1] Loading & splitting...")
docs = TextLoader("data/sample_spec.md", encoding="utf-8").load()
splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=60)
chunks = splitter.split_documents(docs)
print(f"  {len(chunks)} chunks")


# ============================================================
# 2. 建三種 retriever
# ============================================================
print("[2] Building 3 retrievers...")

# (a) Semantic：embedding + Chroma
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(chunks, embeddings)
semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# (b) BM25：傳統關鍵字搜尋（不用 embedding，不花錢）
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 3

# (c) Hybrid：用 EnsembleRetriever 把兩個合在一起，按 RRF 融合
hybrid_retriever = EnsembleRetriever(
    retrievers=[semantic_retriever, bm25_retriever],
    weights=[0.5, 0.5],   # 各占 50%
)


# (d) Hybrid + Reranker：拿 hybrid 的 top-N，用 cross-encoder 重排成 top-K
#     這是 production RAG 的標配做法
print("  Loading reranker model (first run downloads ~4MB)...")

# 把 hybrid 改成回傳更多（top-8），給 reranker 更大池子
hybrid_for_rerank = EnsembleRetriever(
    retrievers=[
        vectorstore.as_retriever(search_kwargs={"k": 5}),
        BM25Retriever.from_documents(chunks),
    ],
    weights=[0.5, 0.5],
)
hybrid_for_rerank.retrievers[1].k = 5

reranker = FlashrankRerank(top_n=3)   # 重排後只保留 top-3
hybrid_rerank_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=hybrid_for_rerank,
)


# ============================================================
# 3. 用 3 個對比性 query 測試
# ============================================================
queries = [
    # Query 1：「概念性」問題 — semantic 應該強，BM25 可能弱
    "How to handle clock crossing safely?",

    # Query 2：「冷僻關鍵字」問題 — BM25 應該強，semantic 可能弱
    "always_ff",

    # Query 3：「同義詞」問題 — semantic 應該強（power consumption ≠ energy use 字面）
    "energy usage of the hash module",
]


def show(name: str, results):
    print(f"\n  [{name}] top-{len(results)}")
    for i, doc in enumerate(results, 1):
        # 抓前 80 字，去掉換行方便看
        preview = doc.page_content.replace("\n", " ")[:90]
        print(f"    {i}. {preview}...")


for q in queries:
    print("\n" + "=" * 70)
    print(f"QUERY: {q}")
    print("=" * 70)
    show("Semantic", semantic_retriever.invoke(q))
    show("BM25",     bm25_retriever.invoke(q))
    show("Hybrid",   hybrid_retriever.invoke(q))
    show("Hybrid+Rerank", hybrid_rerank_retriever.invoke(q))
