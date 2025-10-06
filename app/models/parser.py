from .models import Test, Question
import re

TOPIC_RE = "^=(.*)"
QUESTION_RE = "^([!#])"

# def parse_test(string: str) -> Test:
#    re.split(TOPIC_RE, string)