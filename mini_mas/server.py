from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from mini_mas.events import sse_event
from mini_mas.orchestrator import Orchestrator

app = FastAPI(title="mini_mas")
FRONTEND = Path(__file__).parent.parent / "frontend" / "index.html"

class ChatRequest(BaseModel):
    query : str

@app.get("/api/health")
def health():
    return {"status":"ok"}

@app.get("/")
def index():
    return FileResponse(FRONTEND)

@app.post("/api/chat")
async def chat(req:ChatRequest) :
    async def event_stream():
        orch = Orchestrator()
        try:
            async for event in orch.astream(req.query):
                if event["event"] == "done":
                    continue
                yield sse_event(event["event"], event["data"])
        except Exception as e:
            yield sse_event("status", {"code":"9999", "error":f"{type(e).__name__}: {e}"})
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
