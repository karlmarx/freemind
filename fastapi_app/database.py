from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# make this work with docker and env variables and maybe proxy?
from sqlalchemy.pool import NullPool

load_dotenv()
# db_username = os.environ.get('DB_USERNAME')
# db_password = os.environ.get('DB_PASSWORD')
db_username = 'karl'
db_password = 'a504202A!'

basedir = os.path.abspath(os.path.dirname(__file__))
# SQLALCHEMY_DATABASE_URL= 'sqlite:///' + os.path.join(basedir, 'freemind.db')
# SQLALCHEMY_DATABASE_URL = f'postgresql://{db_username}:{db_password}@localhost:5432/freemind'
SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASEURL')

engine = create_engine(
    # SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=2,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_use_lifo=True,

)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
