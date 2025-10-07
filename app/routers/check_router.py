
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..models.models import Seance, Ticket
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
    Усі сеанси, відкриті поточному юзеру.
    """

        
    all_seances = db.query(Seance).all()

   
    seances = [s for s in all_seances if s.username == user.username]
    seances = [s for s in seances if s.open_time + timedelta(minutes=s.open_minutes > datetime.now())] 

    return templates.TemplateResponse("check/open_list.html", {"request": request, "seances": seances})




@router.get("/to_test/{seance_id}")
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
    
    return templates.TemplateResponse("check/to_test.html", {"request": request})