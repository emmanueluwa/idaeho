from dotenv import load_dotenv

load_dotenv()

from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from models.audio import Audios
from pydantic import BaseModel

from database.db import create_tables, get_db

create_tables()

app = FastAPI(
    title="Idaeho",
    description="play audio files",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# middleware

# routes


@app.get("/")
async def get_all_audio_files(db: Annotated[Session, Depends(get_db)]):
    return db.query(Audios).all()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=0000, reload=True)
