from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models.models import Base, Ticket

# Створюємо engine (SQLite файл лежить у /data/PSS.db)
engine = create_engine(
    "sqlite:////data/Checking.db",
    echo=True,
    connect_args={"check_same_thread": False}  # потрібно для SQLite + багатопоточного доступу
)

# Створюємо фабрику сесій
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency для роутерів
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(engine)

