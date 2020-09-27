from typing import List, Optional

from sqlalchemy_utils import EmailType

# from models import Role
from datetime import date, time, timedelta
from enum import Enum, IntEnum

from pydantic import BaseModel, EmailStr


class Role(str, Enum):
    owner = "owner"
    admin = "admin"
    teacher = "teacher"
    staff = "staff"
    student = "student"

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    roles: List[Role]
    dob: Optional[date] = None

class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
        use_enum_values = True


class UserInDB(User):
    # better name later.  just to match oauth tutorial
    password: str


class ClassBase(BaseModel):
    # TODO: make a configurable default for this and maybe store in a table?
    classSize: int
    waitlistSize: Optional[int] = 0
    name: str
    description: Optional[str] = ""


class ClassCreate(ClassBase):
    pass


class Class(ClassBase):
    id: int

    class Config:
        orm_mode = True


class ScheduledClass(BaseModel):
    startTime: time
    duration: Optional[timedelta] = timedelta(minutes=60)

    """
    roles : List(Role)
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
    """
