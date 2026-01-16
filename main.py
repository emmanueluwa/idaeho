from dotenv import load_dotenv

load_dotenv()

from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, audio


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
    allow_origins=["http://localhost:8080", "https://customdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(audio.router, prefix="/api/audio", tags=["Audio"])


@app.get("/", tags=["Health"])
async def root():
    """
    health check
    """
    return {"status": "online", "message": "idaeho api is running", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
