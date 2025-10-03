""" All models for PSS.db """
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import ForeignKey, String, DateTime, Integer, Text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass

class Test(Base):
    __tablename__ = "tests"

    title: Mapped[str] = mapped_column(String, primary_key=True)  # назва
    username: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(String)
    # nav
    questions: Mapped[List["Question"]] = relationship(back_populates="test")
    seances: Mapped[List["Seance"]] = relationship(back_populates="test")
    
class Question(Base):
    __tablename__ = "questions"

    test_title: Mapped[str] = mapped_column(ForeignKey("tests.title", ondelete="CASCADE"), primary_key=True)  # назва
    number: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String)              # '!', '#' 
    text: Mapped[str] = mapped_column(Text)
    answers: Mapped[str] = mapped_column(Text) 
    # nav           
    test: Mapped["Test"] = relationship(back_populates="questions")

class Seance(Base):
    __tablename__ = "seances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) 
    test_title: Mapped[str] = mapped_column(String, ForeignKey("tests.title", ondelete="CASCADE"),)
    tutor_name: Mapped[str] = mapped_column(String)
    open_time: Mapped[datetime] = mapped_column(DateTime, default=None)
    open_minutes: Mapped[int] = mapped_column(Integer, default=0)
    stud_filter: Mapped[str] = mapped_column(String, default='')
    # nav
    test: Mapped["Test"] = relationship(back_populates="seances")
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="seance", )

class Ticket(Base):
    __tablename__ = "tickets"
 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) 
    seance_id: Mapped[int] = mapped_column(Integer, ForeignKey("seances.id", ondelete="CASCADE"))
    username: Mapped[str] = mapped_column(String)
    test_title: Mapped[str] = mapped_column(String)
    seance_close_time: Mapped[datetime] = mapped_column(DateTime, default=None)
    questions_number: Mapped[int] = mapped_column(Integer)
    next_question_number: Mapped[int] = mapped_column(Integer) 
    protocol: Mapped[str] = mapped_column(Text) 
    #  nav
    seance: Mapped["Seance"] = relationship(back_populates="tickets")

    

    
