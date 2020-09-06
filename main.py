import webbrowser
from typing import List
import os

import logging
import sys
from pprint import pformat
from loguru import logger
from loguru._defaults import LOGURU_FORMAT

import uvicorn
import random
from fastapi import Depends, FastAPI, HTTPException, Request
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
import aiofiles
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import crud
import schemas
import models
import database


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.

    Example:
    >>> payload = [{"users":[{"name": "Nick", "age": 87, "is_active": True}, {"name": "Alex", "age": 27, "is_active": True}], "count": 2}]
    >>> logger.bind(payload=).debug("users payload")
    >>> [   {   'count': 2,
    >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """
    format_string = LOGURU_FORMAT

    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string


# set loguru format for root logger
logging.getLogger().handlers = [InterceptHandler()]

# set format
logger.configure(
    handlers=[{"sink": sys.stdout, "level": logging.DEBUG, "format": format_record}]
)

models.database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="bakasana",
    version="0.0.1",
    description="free webapp/api for yoga studios operational management."
)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/random", response_class=HTMLResponse)
async def randomize_names(request: Request):
    names = ['Gerald', 'Roger', 'Karl', 'Jared', 'Hiren']
    random.shuffle(names)
    logger.info("names served")
    return templates.TemplateResponse("names.html", {'request': request, 'name_array': names})


@app.get("/random/{choices}", response_class=HTMLResponse)
async def randomize_names(request: Request, choices: str):
    choices_list = choices.split(",")
    random.shuffle(choices_list)
    logger.info(f"choices served: {choices}")
    return templates.TemplateResponse("names.html", {'request': request, 'name_array': choices})


def fake_decode_token(token):
    return schemas.User(first_name="karl", last_name="marx", email="fakedecoded" + token)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)


@app.get("/users/me", response_model=schemas.User)
async def get_user_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered.")
    return crud.create_user(db, user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return db_user


#
# @app.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):


if __name__ == '__main__':
    webbrowser.open('http://localhost:8000/docs')
    uvicorn.run(app, host="localhost", port=8000)
