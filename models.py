import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Unicode, Date
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
    first_name = Column(Unicode(50))
    last_name = Column(Unicode(50))
    email = Column(Unicode(50))
    hashed_password = Column(Unicode(50))
    # password = Column(PasswordType)
    dob = Column(Date)
    is_active = Column(Boolean, default=True)


class Class(database.Base):
    __tablename__ = 'class'
    id = Column(Integer, primary_key=True)
    classSize = Column(Integer)
    waitlistSize = Column(Integer)
    name = Column(Unicode(50))
    description = Column(Unicode(300))
