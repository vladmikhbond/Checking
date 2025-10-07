
from ..models.models import Question
import re

def parse_test_body(string: str)->list[Question]:
    RE = r"^=(.*)"
    arr = re.split(RE, string, flags=re.MULTILINE)
    arr = [x.strip() for x in arr if x.strip() != ""]
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

   
def parse_question(kind, question) -> tuple[str, str, str]:
   RE = r"^[^+^-]*"
   m = re.match(RE, question, flags=re.MULTILINE)
   text = question[0:m.span()[1]]
   answers = question[m.span()[1]::]
   return kind, text, answers


# -------------------------- unit test ------------
if (__name__ == "__main__"):
    from models import Question
    x = parse_test(T)
    print(x)

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

