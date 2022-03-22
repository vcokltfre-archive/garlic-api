from typing import Awaitable, Callable
from os import environ

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from src.impl.auth import KeyManager
from src.impl.database import database
from src.impl.types import Request
from src.impl.users import UserManager

from .routes import router

app = FastAPI()
app.include_router(router)

origins = environ["ORIGINS"].split(";")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

users = UserManager()
auth = KeyManager(users)


@app.on_event("startup")  # type: ignore
async def startup() -> None:
    await database.connect()


@app.middleware("http")  # type: ignore
async def add_state(req: Request, nx: Callable[[Request], Awaitable[Response]]) -> Response:
    req.state.auth = auth
    req.state.users = users

    return await nx(req)
