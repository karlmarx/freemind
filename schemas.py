from typing import List, Optional

from sqlalchemy_utils import EmailType

# from models import Role
from datetime import date, time, timedelta
from enum import Enum, IntEnum

from pydantic import BaseModel, EmailStr, Field


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


# class UserUpdate(UserBase):
#     password: Optional[str] = None


class UserPatch(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: Optional[List[Role]] = None
    dob: Optional[date] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
        use_enum_values = True
        schema_extra = {
            "example": {
                "id": 123456,
                "first_name": "Sven",
                "last_name": "Svensson",
                "email": "sven.svensson@example.com",
                "dob": "2020-11-01",
                "roles": [
                    "owner"
                ],
                "is_active": True,
            }
        }


class UserInDB(User):
    # better name later.  just to match oauth tutorial
    hashed_password: str


class ClassBase(BaseModel):
    # TODO: make a configurable default for this and maybe store in a table?
    classSize: int = Field(..., gt=0, description="The class size must be greater than zero")
    waitlistSize: Optional[int] = 0
    name: str
    description: Optional[str] = ""


class ClassCreate(ClassBase):
    pass


class Class(ClassBase):
    id: int

    class Config:
        orm_mode = True

        schema_extra = {
            "example": {
                "id": 108,
                "name": "string",
                "description": "string",
                "classSize": 0,
                "waitlistSize": 0,
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class ScheduledClassBase(BaseModel):
    startTime: time
    teacher: User = None
    classType: Class = None


class ScheduledClassCreate(ScheduledClassBase):
    duration: Optional[timedelta] = timedelta(minutes=60)


class ScheduledClass(ScheduledClassBase):
    endTime: time
    scheduled_students: List[User] = []

    class Config:
        orm_mode = True

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


class Course(BaseModel):
    # id: int
    courseName: str

    class Config:
        orm_mode = True
