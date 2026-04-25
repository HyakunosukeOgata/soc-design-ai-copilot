"""CLI to launch the FastAPI server."""
import uvicorn


def serve():
    """Run: copilot-serve"""
    uvicorn.run(
        "soc_copilot.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    serve()
