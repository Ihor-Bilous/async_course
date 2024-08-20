from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class MessageResponse(BaseModel):
    message: str


@app.get("/", response_model=MessageResponse)
def read_root() -> MessageResponse:
    return MessageResponse(message="Hello, World!")
