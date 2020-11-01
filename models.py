import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Unicode,
    Date,
    DateTime,
    func, Table, PrimaryKeyConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy_enum_list import EnumListType
from sqlalchemy_utils import EmailType, PasswordType
from sqlalchemy.orm import relationship
import database
from schemas import Role

student_roster_table = Table('student_roster', database.Base.metadata,
                             Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
                             Column('scheduled_class_id', Integer, ForeignKey('scheduled_class.id'), nullable=False),
                             PrimaryKeyConstraint('user_id', 'scheduled_class_id')
                             )

# db models
class User(database.Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    roles = Column(EnumListType(Role, str))
    first_name = Column(String)
    last_name = Column(String)
    email = Column(EmailType, unique=True, index=True)
    hashed_password = Column(String)
    # password = Column(PasswordType)
    dob = Column(Date)
    is_active = Column(Boolean, default=True)
    last_modified = Column(
        "last_modified", DateTime, onupdate=datetime.now, default=datetime.now()
    )

    teaching_schedule = relationship("scheduled_class", back_populates="teacher")
    student_schedule = relationship("scheduled_class", secondary="student_roster", back_populates="scheduled_students")


class Class(database.Base):
    __tablename__ = "class"
    id = Column(Integer, primary_key=True)
    classSize = Column(Integer)
    waitlistSize = Column(Integer)
    name = Column(Unicode(50))
    description = Column(Unicode(300))
    last_modified = Column(
        "last_modified", DateTime, onupdate=datetime.now, default=datetime.now()
    )


class ScheduledClass(database.Base):
    __tablename__ = "scheduled_class"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("class.id"))
    last_modified = Column(
        "last_modified", DateTime, onupdate=datetime.now, default=datetime.now()
    )
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    teacher = relationship("users", back_populates="teaching_schedule")
    # class_template = relationship("class", back_populates="teaching_schedule")
    scheduled_students = relationship("users", secondary="student_roster", back_populates="student_schedule")


class Course(database.Base):
    __tablename__ = "course"
    id = Column(Integer, primary_key=True)
    courseName = Column(Unicode(150))
    last_modified = Column(
        "last_modified", DateTime, onupdate=datetime.now, default=datetime.now()
    )
