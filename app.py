from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

from motor_fast import predict
from storage import append, now_iso

app = FastAPI(title="Motor de Predição de Ação")


class InputData(BaseModel):
    problem: str
    goal: str
    pain: str
    today: str


class ResultData(BaseModel):
    problem: str
    category: str
    chosen_action: str
    result_score: int
    would_repeat: bool


@app.get("/")
def health():
    return {"ok": True}


@app.post("/fast")
def fast():
    return {
        "status": "instant",
        "action": "Execute o menor passo agora",
        "confidence": 0.3
    }


@app.post("/predict")
async def do_predict(data: InputData):
    records_tuple = tuple()

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        predict,
        data.problem,
        data.goal,
        data.pain,
        data.today,
        records_tuple
    )
    return result


@app.post("/result")
def save_result(data: ResultData):
    record = {
        "timestamp": now_iso(),
        "problem": data.problem,
        "category": data.category,
        "chosen_action": data.chosen_action,
        "result_score": int(data.result_score),
        "would_repeat": bool(data.would_repeat)
    }
    append(record)
    return {"ok": True}
