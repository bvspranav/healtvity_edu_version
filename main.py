from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import SymptomRequest, SymptomResponse
import llm_client, storage, utils, config
from storage import JSONStorage
from datetime import datetime
import uuid

app = FastAPI(title="Healthcare Symptom Checker (Educational)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_history = JSONStorage(config.HISTORY_FILE)

@app.post("/symptom", response_model=SymptomResponse)
def analyze_symptom(req: SymptomRequest):
    text = utils.normalize_text(req.text)
    if not text or len(text) < 3:
        raise HTTPException(status_code=400, detail="Symptom text is empty or too short.")

    # call llm
    result = llm_client.call_llm(text)

    # store in history
    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": req.user_id,
        "text": text,
        "result": result
    }
    _history.append(record)

    # wrap response
    resp = {
        "conditions": result.get("conditions", []),
        "recommendations": result.get("recommendations", ""),
        "follow_up": result.get("follow_up"),
        "disclaimer": result.get("disclaimer")
    }
    return resp

@app.get("/history")
def get_history():
    return _history.all()

@app.get("/")
def root():
    return {"ok": True, "note": "This is an educational symptom checker API. See /docs for API docs."}
