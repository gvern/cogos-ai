from fastapi import FastAPI, Query
from pydantic import BaseModel
from core.memory import query_memory
from core.reflector import reflect_on_last_entries, summarize_by_tag
from core.context_loader import get_raw_context

app = FastAPI(title="CogOS API")

class QueryRequest(BaseModel):
    question: str

@app.get("/ping")
def ping():
    return {"status": "CogOS is alive 🔥"}

@app.post("/query")
def query(req: QueryRequest):
    return {"response": query_memory(req.question)}

@app.get("/reflect")
def reflect():
    return {"summary": reflect_on_last_entries()}

@app.get("/summarize_tag")
def summarize(tag: str = Query(...)):
    return {"summary": summarize_by_tag(tag)}

@app.get("/context")
def get_context():
    return get_raw_context()
