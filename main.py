import webbrowser
from typing import List
import os

import uvicorn
import random
from fastapi import Depends, FastAPI, HTTPException, Request
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
import aiofiles
from sqlalchemy.orm import Session

import crud
import schemas
import models
import database

models.database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="bakasana",
    version="0.0.1",
    description="free webapp/api for operating yoga studios."
)
app.mount("/static", StaticFiles(directory="static"), name="app/static")

templates = Jinja2Templates(directory="templates")


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
    return templates.TemplateResponse("names.html", {'request': request, 'name_array': names})


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
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


if __name__ == '__main__':
    webbrowser.open('http://localhost:8000/docs')
    uvicorn.run(app, host="localhost", port=8000)
