"""Document ingestion: load -> split -> embed -> in-memory Chroma.

Returns (chunks, vectorstore) so retrievers can be built on top.
"""
from pathlib import Path
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from soc_copilot.config import (
    DEFAULT_DOC, EMBED_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
)


def _load_one(path: Path):
    if path.suffix.lower() == ".pdf":
        return PyPDFLoader(str(path)).load()
    return TextLoader(str(path), encoding="utf-8").load()


def build_index(
    doc_path: Path | str = DEFAULT_DOC,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
):
    """Load + split + embed a single document into an in-memory Chroma index.

    Returns:
        (chunks, vectorstore): chunks for BM25, vectorstore for semantic.
    """
    docs = _load_one(Path(doc_path))
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings(model=EMBED_MODEL)
    vs = Chroma.from_documents(chunks, embeddings)
    return chunks, vs


def main():
    """CLI entry: report chunk count for the default doc."""
    chunks, _ = build_index()
    print(f"Built index with {len(chunks)} chunks from {DEFAULT_DOC.name}")


if __name__ == "__main__":
    main()
