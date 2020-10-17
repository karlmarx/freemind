import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Unicode, Date, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy_enum_list import EnumListType
from sqlalchemy_utils import EmailType, PasswordType
from sqlalchemy.orm import relationship
import database
from schemas import Role


# db models
class User(database.Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    roles = Column(EnumListType(Role, str))
    first_name = Column(String)
    last_name = Column(String)
    email = Column(EmailType, unique=True, index=True)
    hashed_password = Column(String)
    # password = Column(PasswordType)
    dob = Column(Date)
    is_active = Column(Boolean, default=True)
    last_modified = Column('last_modified', DateTime, onupdate=datetime.now, default=datetime.now())


class Class(database.Base):
    __tablename__ = 'class'
    id = Column(Integer, primary_key=True)
    classSize = Column(Integer)
    waitlistSize = Column(Integer)
    name = Column(Unicode(50))
    description = Column(Unicode(300))
    last_modified = Column('last_modified', DateTime, onupdate=datetime.now, default=datetime.now())


class Course(database.Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    courseName = Column(Unicode(150))
    last_modified = Column('last_modified', DateTime, onupdate=datetime.now, default=datetime.now())
