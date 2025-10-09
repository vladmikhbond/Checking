from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import APIKeyCookie

from jose import jwt
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.models import Test, Seance, Ticket
from app.routers.login_router import get_current_user
from ..dal import get_db  # Функція для отримання сесії БД
from ..models.pss_models import User
from ..models.utils import str_to_time, time_to_str


# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- list

@router.get("/ticket/list/{seance_id}")
async def get_ticket_list(
    seance_id:int,
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    """ 
    Список тікетів певного сеансу.
    """
    # return the login page with error message
    if user.role != "tutor":
        return templates.TemplateResponse(
            "../login/login.html", 
            {"request": request, "error": user.role})
        
    seance = db.get(Seance, seance_id)    
    return templates.TemplateResponse("ticket/list.html", {"request": request, "seance": seance})

# ------- del 

@router.get("/ticket/del/{id}")
async def get_ticket_del(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    """ 
    Видалення тікету.
    """
    # return the login page with error message
    if user.role != "tutor":
        return templates.TemplateResponse(
            "../login/login.html", 
            {"request": request, "error": user.role})

    ticket = db.get(Ticket, id)
    if not ticket:
        return RedirectResponse(url=f"/ticket/list/{ticket.seance_id}", status_code=302)
   
    return templates.TemplateResponse("ticket/del.html", {"request": request, "ticket": ticket})


@router.post("/ticket/del/{id}")
async def post_ticket_del(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    ticket = db.get(Ticket, id)
    db.delete(ticket)
    db.commit()
    return RedirectResponse(url=f"/ticket/list/{ticket.seance_id}", status_code=302)

