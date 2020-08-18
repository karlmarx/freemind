import webbrowser
import fastapi

from fastapi import FastAPI, APIRouter
from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from sqlalchemy import Column, Integer, String, Float, Table, ForeignKey, Unicode, Date
import os, enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_enum_list import EnumListType
from sqlalchemy_utils import EmailType, PasswordType, PhoneNumberType, force_auto_coercion
import click
from flask.cli import with_appcontext

app = FastAPI()

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URL =  'sqlite:///' + os.path.join(basedir, 'freemind.db')


# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



def db_create():
    db.create_all()
    print("db created")


def db_drop():
    db.drop_all()
    print('db dropped')


def db_seed():
    jane_owner = User(first_name="jane", last_name="doe", email="email@email.org", password="Password1234", roles=[Role.admin,Role.owner,Role.teacher,Role.staff,Role.student])
    db.session.add(jane_owner)
    db.session.commit()
    print('db seeded')



@app.get('/')
def hello_world():
    return 'Hello World!'

class Role(enum.Enum):
    owner = 0
    admin = 1
    teacher = 2
    staff = 3
    student = 4

#db models
class User(Base):
    __tablename__: 'users'
    id = Column(Integer, primary_key=True)
    roles = Column(EnumListType(Role, int))
    first_name = Column(Unicode(50))
    last_name = Column(Unicode(50))
    email = Column(EmailType)
    password = Column(PasswordType(schemes=[
            'pbkdf2_sha512',
            'md5_crypt'
        ]))
    # password = Column(PasswordType)
    dob = Column(Date)


# class Role(Base):
#     __tablename__: 'role'
#     id = Column(Integer, primary_key=True)
#     label = Column(String)
#
# db_drop()
# db_create()
# db_seed()

if __name__ == '__main__':
    webbrowser.open('http://localhost:5000')
    app.run()


