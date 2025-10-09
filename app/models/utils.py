import json
from zoneinfo import ZoneInfo
from datetime import datetime

from ..models.models import Question

#---------------------------------------------------------

FMT = "%Y-%m-%dT%H:%M"
ZONE = "Europe/Kyiv"

def time_to_str(dt: datetime) -> str:
    return dt.astimezone(ZoneInfo(ZONE)).strftime(FMT)

def str_to_time(s: str) -> datetime:
    return datetime.strptime(s, FMT) \
        .replace(tzinfo=ZoneInfo(ZONE)) \
        .astimezone(ZoneInfo("UTC"))

#---------------------------------------------------------

def result_in_procents(protocol: str, questions: list[Question]) -> int:
    sum = 0
    prot_arr = protocol.strip().replace("'", "").split('\n')  # ["[1]", "[4]", "[1, 3]"]
    questions.sort(key=lambda q: q.number)
    n = len(prot_arr)
    for i in range(n):
        record = prot_arr[i]                                  # "[1, 3];120"
        user_choice = record.split(';')[0]                    # "[1, 3]"
        user_set = set(json.loads(user_choice))               # {1, 3} 

        author_set:set = set(); 
        arr = questions[i].answers.split('\n')                # ["+apple", "-bottle", "+cherry"]
        for i, s in enumerate(arr, start=1):
            if s.startswith('+'):
                author_set.add(i)                             # {1, 3}
         
        if (user_set == author_set):
            sum += 1 
    return (100 * sum + 0.5) // n 
    
