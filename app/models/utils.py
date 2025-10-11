import json, re
from zoneinfo import ZoneInfo
from datetime import datetime

from ..models.models import Question
# from models import Question              # for testing

#--------------------------------- time <-> str ------------------------  

FMT = "%Y-%m-%dT%H:%M"
ZONE = "Europe/Kyiv"

def time_to_str(dt: datetime) -> str:
    return dt.astimezone(ZoneInfo(ZONE)).strftime(FMT)

def str_to_time(s: str) -> datetime:
    return datetime.strptime(s, FMT) \
        .replace(tzinfo=ZoneInfo(ZONE)) \
        .astimezone(ZoneInfo("UTC"))

#---------------------------------------------------------

class Result:
    quest_text: str
    quest_kind: str
    u_sign: list[str]
    a_sign: list[str]
    answers: list[str]
    seconds: float
    focuse_lost: int

    def __init__(self, quest: Question, record,             # "[1, 3];120;1"
    ):
        ans_arr = quest.answers.strip().splitlines()
        n = len(ans_arr)
        self.a_sign = [x[0] for x in ans_arr]               #['+', '-', '+']

        m = re.fullmatch(r"(\[.*\]);(\d+);(\d*)", record, )   
        m1 = json.loads(m[1])                               # m[1] = [1, 3]    
        self.u_sign = ['-'] * n
        for i in m1:
            self.u_sign[i-1] = '+'                          #['+', '-', '+']

        self.seconds = int(m[2])
        self.focuse_lost = int(m[3])
        self.quest_text = quest.text
        self.quest_kind = quest.kind
        self.answers = [a[1::] for a in ans_arr]
        pass
    
    def score(self):
        return 1 if self.a_sign == self.u_sign else 0
    

def test_result(protocol: str, questions: list[Question]) -> int:
    
    records = protocol.strip().replace("'", "").splitlines() 
    seconds_0 = int(records[0])
    questions.sort(key=lambda q: q.number)

    results = []
    for i, question in enumerate(questions, start=1):
        res = Result(question, records[i])
        res.seconds -= seconds_0
        seconds_0 += res.seconds
        results.append(res)
    
    summa = sum(x.score() for x in results)

    score = round(100 * summa / len(questions), 0) 
    return score, results 

# -------------------------------------------------------

if __name__ == "__main__":
    Result(
        Question(kind='#', text="Доколе?", answers="+apple\n-table\n+cherry\n"),
        "[1, 3];120;1"   
    )


