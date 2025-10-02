from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlmodel import select

from auth.auth import authenticate_user, create_access_token, get_current_user
from models.models import User, Task, TaskTag, TimeLog, Tag
from database.connection import init_db, get_session
from models.schemas import *
from auth.security import *
from routers.api import router


app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"Ура, приложение тайм менеджмента запустилось!"}


app.include_router(router)