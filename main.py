from dotenv import load_dotenv

load_dotenv()

from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Idaeho",
    description="play audio files",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    health check
    """
    return {"status": "online", "message": "idaeho api is running", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=0000, reload=True)
