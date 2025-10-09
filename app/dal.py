from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from sqlalchemy import event
from sqlalchemy.engine import Engine

CON_STR = "sqlite:////data/CHECKING.db"

# Підтримка foreign keys для SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Створюємо engine (SQLite файл лежить у /data/PSS.db)
engine = create_engine(
    CON_STR,
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

# ================================================================

engine_pss = create_engine(
    "sqlite:////data/PSS.db",
    echo=True,
    connect_args={"check_same_thread": False}  # потрібно для SQLite + багатопоточного доступу
)

SessionLocalPss = sessionmaker(autocommit=False, autoflush=False, bind=engine_pss)

def get_db_pss():
    db: Session = SessionLocalPss()
    try:
        yield db
    finally:
        db.close()

# ================================================================



T1 = """
=класи

!Оберіть вірне

class Point:
    x = 0
    y = 0 	

    def __init__(self):
        self.x = 0
        self.z = 0

+в коді визначено 2 поля класу і 2 поля екземпляру
-в коді визначено 2 поля класу і 1 полe екземпляру
-в коді визначено 1 полe класу і 2 поля екземпляру
-в коді визначено 0 полів класу і 4 поля екземпляру


! За замовчанням метод __eq__() ...

+вважає об'єкт екземпляру рівним тільки самому собі
-для порівняння екземплярів користується віддзеркаленням
-взагалі не реалізований 
-вважає рівними усі екземпляри одного класу


! Методи екземпляру в Пітоні 

+є віртуальними
-є невіртуальними
-можуть бути як віртуальними, так і невіртуальними


! Що потрібно вчинити, щоб приховати атрибут класу?

+розпочати його ім'я з подвійного підкреслення
-закінчити його ім'я подвійним підкресленням
-оточити його ім'я подвійними підкресленнями
-застосувати до атрибуту специфікатор private

"""
T2 = """

=фруктии

#Оберіть фрукти

+apple
-bottle
+cherry"

! За замовчанням метод __str__() ...

-повертає рядок з інформацією про стан екземпляру
-взагалі не реалізований 
-вважає об'єкт екземпляру рівним тільки самому собі
+повертає назву типу і ціле число
-повертає рядок з якого можна відтворити екземпляр

! Методи класу в в Пітоні 

+є віртуальними
-є невіртуальними
-можуть бути як віртуальними, так і невіртуальними

# Які декоратори знадобляться, щоб визначити властивість abc,
яку можна читати, писати і видаляти?

+@property
-@abc.getter
+@abc.setter
+@abc.deleter

"""

# from models.models import Base, Test, Ticket
# if __name__ == "__main__":
#     Base.metadata.create_all(engine)

