"""Centralized configuration: paths, model names, chunk params.

All other modules import from here so we change settings in ONE place.
"""
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------- Paths ----------
ROOT = Path(__file__).resolve().parents[2]  # repo root (src/soc_copilot/config.py -> ../../..)
DATA_DIR = ROOT / "data"
EVAL_DIR = ROOT / "eval"
GOLDEN_PATH = EVAL_DIR / "golden.jsonl"
REPORTS_DIR = EVAL_DIR / "reports"

DEFAULT_DOC = DATA_DIR / "sample_spec.md"

# ---------- Models ----------
LLM_MODEL = "gpt-4o-mini"
EMBED_MODEL = "text-embedding-3-small"
JUDGE_MODEL = "gpt-4o-mini"
RERANKER_MODEL = "ms-marco-MultiBERT-L-12"

# ---------- Chunking ----------
CHUNK_SIZE = 400
CHUNK_OVERLAP = 60

# ---------- Retrieval ----------
DEFAULT_K = 3
RERANK_POOL_K = 5  # how many candidates feed the reranker
