from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import APIKeyCookie

from jose import jwt
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.models import Test, Seance
from app.routers.login_router import get_current_user
from ..dal import get_db  # Функція для отримання сесії БД
from ..models.pss_models import User
from ..models.utils import str_to_time, time_to_str


# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- list

@router.get("/seance/list")
async def get_seance_list(
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    """ 
    Усі сеанси поточного юзера (викладача).
    """
    # return the login page with error message
    if user.role != "tutor":
        return templates.TemplateResponse(
            "../login/login.html", 
            {"request": request, "error": user.role})
        
    all_seances = db.query(Seance).all()

    seances = [s for s in all_seances if s.username == user.username ] 
    return templates.TemplateResponse("seance/list.html", {"request": request, "seances": seances})

# ------- new 

@router.get("/seance/new")
async def get_seance_new(
    request: Request,
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    """ 
    Створення нового сеансу поточного юзера (викладача). 
    """
    tests = db.query(Test).all()
    seance = Seance(
        username = user.username, 
        open_time = time_to_str(datetime.now()),  
        open_minutes = 0,
        stud_filter = ""
    )
    return templates.TemplateResponse("seance/new.html", {"request": request, "seance": seance, "tests": tests})


@router.post("/seance/new")
async def post_seance_new(
    request: Request,
    test_id: int = Form(...),
    open_time: str = Form(...),
    open_minutes: int = Form(...),
    stud_filter: str = Form(...),
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    seance = Seance(
        test_id = test_id,
        username = user.username, 
        open_time = str_to_time(open_time),
        open_minutes = open_minutes,
        stud_filter = stud_filter,
    )
    try:
        db.add(seance)                        
        db.commit()
    except Exception as e:
        db.rollback()
        err_mes = f"Error during a new seance adding: {e}"
        print(err_mes)
        tests = db.query(Test).all()
        return templates.TemplateResponse("seance/new.html", {"request": request, "seance": seance, "tests": tests})

    return RedirectResponse(url="/seance/list", status_code=302)


# ------- edit 

@router.get("/seance/edit/{id}")
async def get_seance_edit(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    """ 
    Редагування сеансу.
    """
    seance = db.get(Seance, id)
    seance.open_time = time_to_str(seance.open_time)
    tests = db.query(Test).all()

    if not seance:
        return RedirectResponse(url="/seance/list", status_code=302)
    return templates.TemplateResponse("seance/edit.html", {"request": request, "seance": seance, "tests": tests})


@router.post("/seance/edit/{id}")
async def post_seance_edit(
    id: int,
    request: Request,
    test_id: int = Form(...),
    open_time: str = Form(...),
    open_minutes: int = Form(...),
    stud_filter: str = Form(...),
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    seance = db.get(Seance, id)
    if not seance:
        return RedirectResponse(url="/seance/list", status_code=302)

    seance.username = user.username  
    seance.test_id = test_id
    seance.open_time = str_to_time(open_time)
    seance.open_minutes = open_minutes
    seance.stud_filter = stud_filter
    
    db.commit()
    return RedirectResponse(url="/seance/list", status_code=302)

# ------- del 

@router.get("/seance/del/{id}")
async def get_seance_del(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    """ 
    Видалення сеансу.
    """
    seance = db.get(Seance, id)
    if not seance:
        return RedirectResponse(url="/seance/list", status_code=302)
    return templates.TemplateResponse("seance/del.html", {"request": request, "seance": seance})


@router.post("/seance/del/{id}")
async def post_seance_del(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    seance = db.get(Seance, id)
    db.delete(seance)
    db.commit()
    return RedirectResponse(url="/seance/list", status_code=302)


