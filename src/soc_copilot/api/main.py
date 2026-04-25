"""FastAPI application: /ask, /ask/stream, /health.

Run locally:
    uvicorn soc_copilot.api.main:app --reload

Then:
    curl -X POST http://localhost:8000/ask \
         -H "Content-Type: application/json" \
         -d '{"question":"How does the FIFO handle metastability?"}'
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from soc_copilot.rag import build_index, make_retriever, make_rag_chain
from soc_copilot.rag.chain import REFUSAL_TEXT
from soc_copilot.api.schemas import (
    AskRequest, AskResponse, Source, HealthResponse,
)

# Module-level state — set during lifespan startup
_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the RAG pipeline once at startup; reuse across requests."""
    chunks, vs = build_index()
    retriever = make_retriever("semantic", vs, chunks, k=3)
    chain = make_rag_chain(retriever)
    _state["chunks"] = chunks
    _state["retriever"] = retriever
    _state["chain"] = chain
    print(f"[startup] indexed {len(chunks)} chunks")
    yield
    _state.clear()


app = FastAPI(
    title="SoC Design AI Copilot",
    description="RAG service for SoC/RTL design questions.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        chunks_indexed=len(_state.get("chunks", [])),
    )


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    chain = _state.get("chain")
    retriever = _state.get("retriever")
    if not chain or not retriever:
        raise HTTPException(status_code=503, detail="Index not ready")

    # Run retrieval + generation
    retrieved = await retriever.ainvoke(req.question)
    answer = await chain.ainvoke(req.question)
    refused = REFUSAL_TEXT.lower() in answer.lower()

    return AskResponse(
        answer=answer.strip(),
        sources=[
            Source(content=d.page_content[:300], chunk_id=i)
            for i, d in enumerate(retrieved)
        ],
        refused=refused,
    )


@app.post("/ask/stream")
async def ask_stream(req: AskRequest):
    """Server-Sent Events streaming. Each event is one token chunk."""
    chain = _state.get("chain")
    if not chain:
        raise HTTPException(status_code=503, detail="Index not ready")

    async def event_gen():
        async for token in chain.astream(req.question):
            # SSE format: "data: <payload>\n\n"
            # Escape newlines so multi-line tokens don't break SSE framing.
            safe = token.replace("\n", "\\n")
            yield f"data: {safe}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")
