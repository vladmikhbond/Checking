import re
import itertools as it
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..models.models import Test, Seance, Ticket
from app.routers.login_router import get_current_user
from ..dal import get_db  # Функція для отримання сесії БД
from ..models.pss_models import User


SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- list

@router.get("/check/open_list")
async def get_check_topen_list(
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    """ 
    Усі відкриті сеанси, доступні поточному юзеру (студенту).
    """
    all_seances = db.query(Seance).all()
    seances = []
    for s in all_seances:
        not_expired = s.open_time + timedelta(minutes=s.open_minutes) > datetime.now()
        matched = re.match(s.stud_filter, user.username) 
        if not_expired and matched:
            seances.append(s)

    return templates.TemplateResponse("check/open_list.html", {"request": request, "seances": seances})

# --------------------------- run 

@router.get("/check/run/{seance_id}")
async def get_to_test(
    seance_id: int,
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user) 
):
    seance = db.get(Seance, seance_id)
    tickets = [t for t in seance.tickets if t.username == user.username]
    # ticket exists
    if len(tickets) > 0:
        ticket = tickets[0]
    else:
        ticket = Ticket(
            seance_id = seance.id,
            username = user.username,
            seance_close_time = seance.open_time + timedelta(minutes=seance.open_minutes),
            number_of_questions = len(seance.test.questions),
            next_question_number = 1,
            protocol = ""
        )
        db.add(ticket)
        db.commit()
    # чи не прострочений тікет
    if ticket.seance_close_time < datetime.now():
        raise HTTPException(403, "Час сплив.")
    
    # чи не скінчилися питанняя тесту
    if ticket.next_question_number > ticket.number_of_questions:
        raise HTTPException(403, "скінчилися питанняя тесту.")
    
    # знайти чергове питання
    test = db.get(Test, seance.test_id)
    if not test:
        raise HTTPException(500, "несподівано Тест зник!!!")

    questions = filter(lambda q: q.number == ticket.next_question_number,  test.questions)
    question = next(questions)
    answers = enumerate(question.answers.split('\n'), start=1)

    return templates.TemplateResponse("check/run.html", 
        {"request": request, "question": question, "answers": answers})

@router.post("/check/run/{seance_id}")
async def get_to_test(
    seance_id: int,
    request: Request, 
    # qqq: int = Form(...),
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user) 
):
    form = await request.form()
    qqq = form.getlist('qqq')   


    seance = db.get(Seance, seance_id)
    ticket = [t for t in seance.tickets if t.username == user.username][0]
    # чи не прострочений тікет
    if ticket.seance_close_time < datetime.now():
        raise HTTPException(403, "Час сплив.")
    
    # TODO зберегти відповідь
    ticket.protocol += f"{qqq}\n"    
    ticket.next_question_number += 1 
    db.commit()

    # чи не скінчилися питанняя тесту
    if ticket.next_question_number > ticket.number_of_questions:
        raise HTTPException(403, "скінчилися питанняя тесту.")


    # знайти чергове питання і його відповіді
    test = db.get(Test, seance.test_id)
    if not test:
        raise HTTPException(500, "несподівано Тест зник!!!")

    questions = filter(lambda q: q.number == ticket.next_question_number,  test.questions)
    question = next(questions)
    answers = enumerate(question.answers.split('\n'), start=1)

    return templates.TemplateResponse("check/run.html", 
        {"request": request, "question": question, "answers": answers})