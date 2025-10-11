from fastapi import HTTPException
from ..models.models import Question
import re

# from models import Question  # for unit testing

VALIDATION=False

def ass(x: bool, comment: str) : 
    if not x: 
        raise HTTPException(400, comment)

def parse_test_body(string: str, validation=False)->list[Question]:
    global VALIDATION
    VALIDATION = validation
    RE = r"^=(.*)"
    arr = re.split(RE, string, flags=re.MULTILINE)
    arr = [x.strip() for x in arr if x.strip() != ""]
    if VALIDATION: ######
        ass(len(arr[0::2]) == len(arr[1::2]), "Wrong topic division")
        
    pairs = zip(arr[0::2], arr[1::2])    # [(topicName, topicBody)]
    questions = []
    for name, body in pairs:
        topic_questions = parse_topic_body(name, body)
        questions.extend(topic_questions)
    for i, question in enumerate(questions):
        question.number = i + 1  
    return questions 
   

def parse_topic_body(name, body)->list[Question]:
   RE = r"^([!#])"
   arr = re.split(RE, body, flags=re.MULTILINE)
   arr = [x.strip() for x in arr if x.strip() != ""]
   pairs = zip(arr[0::2], arr[1::2])
   trios = [parse_question(kind, question) for kind, question in pairs]   # [(kind, (text, answers))]
   return [Question(topic=name, kind=t[0], text=t[1], answers=t[2]) for t in trios]

   
def parse_question(kind, quest_body) -> tuple[str, str, str]:
    RE = r"^[^+^-]*"
    match = re.match(RE, quest_body, flags=re.MULTILINE)
    text = quest_body[0:match.span()[1]].strip()
    answers = quest_body[match.span()[1]::].strip()  # "+apple\n-table\n+cherry"
    if VALIDATION: ######
        # count of right answers
        rights = sum(1 if line.startswith('+') else 0 for line in answers.splitlines())  
        ass(kind=='!' and rights==1 or kind=='#', f"Kind Error: \n{quest_body}") 
 
    return kind, text, answers


# -------------------------- unit test ------------
T = """

=класи

!Оберіть вірне

class Point:
    x = 0
    y = 0 	

    def __init__(self):
        self.x = 0
        self.z = 0

+в коді визначено 3 атрибути класу і 2 атрибути екземпляру
-в коді визначено 2 атрибути класу і 2 атрибути екземпляру
-в коді визначено 1 атрибут класу і 4 атрибути екземпляру
-в коді визначено 2 атрибути класу і 3 атрибути екземпляру

==12345

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


if (__name__ == "__main__"):
    
    quests = parse_test_body(T, validation=True)
    print(len(quests))

