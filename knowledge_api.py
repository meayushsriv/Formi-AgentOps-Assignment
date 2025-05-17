from fastapi import FastAPI, Form
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

df = pd.read_csv("faqs.csv")

@app.post("/api/knowledge")
async def get_answer(question: str = Form(...), location: str = Form(None)):
    result = df[df['question'].str.contains(question, case=False, na=False)]
    if location:
        result = result[result['location'].str.lower() == location.lower()]
    return {
        "answer": result.iloc[0]['answer'] if not result.empty else "I don't know"
    }
