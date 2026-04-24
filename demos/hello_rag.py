"""
hello_rag.py — 第一個 RAG pipeline

學習目標：
1. 看懂 5 個零件如何串起來：Loader → Splitter → Embedding → VectorStore → Retriever
2. 體驗 chunking 對 retrieval 品質的影響
3. 對比「有 RAG」vs「沒 RAG」的回答差異
"""
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# ============================================================
# Step 1: Load — 讀文件
# ============================================================
print("[1/5] Loading document...")
loader = TextLoader("data/sample_spec.md", encoding="utf-8")
docs = loader.load()
print(f"  Loaded {len(docs)} document(s), total {len(docs[0].page_content)} chars")


# ============================================================
# Step 2: Split — 把文件切成 chunks
# ============================================================
print("[2/5] Splitting into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,       # 每塊約 400 字（小一點方便觀察）
    chunk_overlap=8,     # 相鄰 chunks 重疊 60 字（避免關鍵句被切斷）
)
chunks = splitter.split_documents(docs)
print(f"  Created {len(chunks)} chunks")
print(f"  First chunk preview: {chunks[0].page_content[:80]}...")


# ============================================================
# Step 3: Embed + Store — 把 chunks 轉成向量存進 Chroma
# ============================================================
print("[3/5] Embedding & storing...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    # 不指定 persist_directory → 記憶體模式，程式結束就消失（教學用）
)
print(f"  Vector store ready ({len(chunks)} vectors)")


# ============================================================
# Step 4: Retriever — 給定 query 回傳最相關的 chunks
# ============================================================
print("[4/5] Setting up retriever...")
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # 取 top-3

# 先單獨測試 retriever，看搜出什麼
test_query = "What is the power consumption of SHA-256?"
print(f"\n  Test retrieval for: '{test_query}'")
retrieved = retriever.invoke(test_query)
for i, doc in enumerate(retrieved):
    print(f"  --- Chunk {i+1} ---")
    print(f"  {doc.page_content[:120]}...")


# ============================================================
# Step 5: RAG Chain — 把 retrieve 的 context 餵給 LLM
# ============================================================
print("\n[5/5] Building RAG chain...")
llm = init_chat_model("openai:gpt-4o-mini")

prompt = ChatPromptTemplate.from_template("""
Answer the question based ONLY on the following context.
If you cannot find the answer in the context, say "I don't know based on the provided documents".

Context:
{context}

Question: {question}

Answer:
""")


def format_docs(docs):
    """把 list of Document → 串成一個大字串給 prompt"""
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


# ============================================================
# 來真的問問題！
# ============================================================
questions = [
    "What is the power consumption of the SHA-256 accelerator?",   # 文件裡有
    "How does the FIFO handle metastability?",                      # 文件裡有
    "What is the read latency of the AXI4-Lite slave?",             # 文件裡有
    "What is the price of NVIDIA H100?",                            # 文件裡沒有
]

for q in questions:
    print("\n" + "=" * 60)
    print(f"Q: {q}")
    print("=" * 60)
    answer = rag_chain.invoke(q)
    print(f"A: {answer}")
