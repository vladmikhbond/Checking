""" All models for PSS.db """
from datetime import datetime, timedelta
from sqlalchemy import ForeignKey, String, DateTime, Integer, Text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass

class Test(Base):
    __tablename__ = "tests"

    id: Mapped[str] = mapped_column(primary_key=True)  # назва
    tutor_id: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(String)
    
