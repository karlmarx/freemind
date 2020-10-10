import webbrowser, time
from datetime import timedelta, datetime
from typing import List, Optional
import os

import logging
import sys
from pprint import pformat

from jose import jwt, JWTError
from loguru import logger
from loguru._defaults import LOGURU_FORMAT

import uvicorn
import random
from fastapi import Depends, FastAPI, HTTPException, Request, status
from pydantic import EmailStr
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
import aiofiles
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

import crud
import schemas
import models
import database

SECRET_KEY = "aca9d760c62d927d401d00832197a2b0fd8342f6f742453647b73eb35d318f98"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {
    "karl@karlmarxindustries.com": {
        "id": 1,
        "first_name": "karl",
        "last_name": "marx",
        "email": "karl@karlmarxindustries.com",
        "hashed_password": "$2b$12$a4xB3.uLILorr2/.MpXoDOTILxC6VbmPFeSkAXIqk4wyIW4C7Uy/u",
        "is_active": True,
        "roles": ["student"]
    },
    "fengels@karlmarxindustries.com": {
        "id": 2,
        "first_name": "friedrich",
        "last_name": "engels",
        "email": "fengels@karlmarxindustries.com",
        "hashed_password": "$2b$12$a4xB3.uLILorr2/.MpXoDOTILxC6VbmPFeSkAXIqk4wyIW4C7Uy/u",
        "is_active": False,
        "roles": ["student"],
    },
}


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    return crud.get_user_by_email(db, username)


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.get("/random", response_class=HTMLResponse)
async def randomize_names(request: Request):
    names = ['Gerald', 'Roger', 'Karl', 'Jared', 'Hiren']
    random.shuffle(names)
    logger.info("names served")
    return templates.TemplateResponse("names.html", {'request': request, 'name_array': names})


@app.get("/random/{choices}", response_class=HTMLResponse)
async def randomize_choices(request: Request, choices: str):
    choices_list = choices.split(",")
    random.shuffle(choices_list)
    logger.info(f"choices served: {choices}")
    return templates.TemplateResponse("names.html", {'request': request, 'name_array': choices_list})




def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=EmailStr(token_data.username))
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def fake_hashed_password(password: str):
    return "fakehashed" + password


@app.get("/users/me", response_model=schemas.User)
async def get_user_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.post("/token")
# TODO: add dependency to check creds in db
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered.")
    return crud.create_user(db, user)


@app.patch("/users/{user_id}", response_model=schemas.User)
def update_user(user_in: schemas.UserPatch, user_id: int, db: Session = Depends(get_db),
                token: str = Depends(oauth2_scheme)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return crud.update_user(db, user_id, user_in)


# @app.put("/users/{user_id}", response_model=schemas.User)
# def create_user(user_in: schemas.UserUpdate, user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found.")
#     return crud.update_user(db, db_user, user_in)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return db_user


@app.middleware("http")
async def add_processing_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Processing-Time"] = str(process_time)
    return response


if __name__ == '__main__':
    # webbrowser.open('http://localhost:8000/docs')
    uvicorn.run(app, host="localhost", port=8000)
