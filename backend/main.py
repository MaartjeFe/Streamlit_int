
from fastapi import FastAPI
from pydantic import BaseModel
from .model import append_suffix

app = FastAPI(title="Append Text API", version="1.0.0")

class AppendRequest(BaseModel):
    text: str
    suffix: str | None = " — processed"

class AppendResponse(BaseModel):
    result: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/append", response_model=AppendResponse)
def append(req: AppendRequest):
    return AppendResponse(result=append_suffix(req.text, req.suffix or " — processed"))
