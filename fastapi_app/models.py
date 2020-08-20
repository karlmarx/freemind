import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Unicode, Date
from sqlalchemy.orm import relationship
from sqlalchemy_enum_list import EnumListType
from sqlalchemy_utils import EmailType, PasswordType
from sqlalchemy.orm import relationship
from .database import Base


class Role(enum.Enum):
    owner = 0
    admin = 1
    teacher = 2
    staff = 3
    student = 4

#db models
class User(Base):
    __tablename__ = 'users'
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
    is_active = Column(Boolean, default=True)