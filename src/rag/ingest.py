"""Document ingestion: load -> split -> embed -> store."""
from pathlib import Path
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from . import config


def load_documents(data_dir: Path = config.DATA_DIR):
    """Walk data_dir and load .md / .txt / .pdf files with source metadata."""
    docs = []
    for p in data_dir.rglob("*"):
        if p.is_dir():
            continue
        suffix = p.suffix.lower()
        try:
            if suffix in (".md", ".txt"):
                loaded = TextLoader(str(p), encoding="utf-8").load()
            elif suffix == ".pdf":
                loaded = PyPDFLoader(str(p)).load()
            else:
                continue
        except Exception as e:
            print(f"[skip] {p}: {e}")
            continue
        for d in loaded:
            d.metadata["source"] = str(p.relative_to(config.ROOT))
        docs.extend(loaded)
    return docs


def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    return splitter.split_documents(docs)


def build_vectorstore(chunks=None):
    """Build a Chroma vectorstore from data_dir (or given chunks)."""
    if chunks is None:
        chunks = split_documents(load_documents())
    emb = OpenAIEmbeddings(model=config.EMBED_MODEL)
    kwargs = {"persist_directory": config.CHROMA_DIR} if config.CHROMA_DIR else {}
    return Chroma.from_documents(chunks, emb, **kwargs)


def main():
    docs = load_documents()
    chunks = split_documents(docs)
    print(f"Loaded {len(docs)} docs -> {len(chunks)} chunks")
    sources = {}
    for c in chunks:
        sources[c.metadata.get("source", "?")] = sources.get(c.metadata.get("source", "?"), 0) + 1
    print("Per-source chunk count:")
    for s, n in sources.items():
        print(f"  {s}: {n}")


if __name__ == "__main__":
    main()
