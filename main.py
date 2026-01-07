from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "obota world"}


class AudibookCreateModel(BaseModel):
    title: str
    author: str


@app.post("/create_audiobook")
async def create_audiobook(audiobook_data: AudibookCreateModel):
    return {"title": audiobook_data.title, "author": audiobook_data.author}
