"""Centralized config (env vars + defaults)."""
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent.parent

# Models
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

# RAG
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 400))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 60))
TOP_K = int(os.getenv("TOP_K", 3))

# Persistence (None = in-memory Chroma)
CHROMA_DIR = os.getenv("CHROMA_DIR")  # e.g. ".chroma"
