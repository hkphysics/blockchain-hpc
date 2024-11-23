#!/usr/bin/env python3
"""Main module."""

import uvicorn
from fastapi import Request, FastAPI
from pydantic import BaseModel
import pydantic_core
import pydantic_quantlib as pql
import json

app = FastAPI()

@app.get("/hello")
def hello_world():
    return "<h2>Hello, World!</h2>"

@app.get("/test")
def test():
    payoff = pql.PlainVanillaPayoff(type=pql.OptionType.Put, strike=40)
    european_exercise = pql.EuropeanExercise(date=pql.Date(d=4, m=1, y=2022))
    european_option = pql.VanillaOptionBase(payoff=payoff, exercise=european_exercise)
    qleo = european_option.to_quantlib()
    return european_option.model_dump()

@app.post("/test1")
async def test1(request: Request):
    model = {k: getattr(pql, k).model_validate(v) for k, v in (await request.json()).items()}
    ql = {k: v.to_quantlib() for k, v in model.items()}
    return {k: v.model_dump() for k, v in model.items()}

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', log_level="debug")
