import os

from fastapi.security import OAuth2PasswordRequestForm
import httpx

from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import APIKeyCookie

from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.models import Test, Seance
from app.routers.login_router import get_current_user
from ..dal import get_db  # Функція для отримання сесії БД
from ..models.pss_models import User
import bcrypt



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
    seance = Seance()  ###########TODO
    tests = db.query(Test).all()

    return templates.TemplateResponse("seance/new.html", {"request": request, "seance": seance, "tests": tests})


@router.post("/seance/new")
async def post_seance_new(
    request: Request,
    test_id: int = Form(...),
    
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    seance = Seance(
        test_id = test_id,
        username = user.username, 

    )
    return seance
    # try:
    #     db.add(seance)                        
    #     db.commit()
    # except Exception as e:
    #     db.rollback()
    #     err_mes = f"Error during a new seance adding: {e}"
    #     return templates.TemplateResponse("seance/new.html", {"request": request, "seance": seance})
    # return RedirectResponse(url="/seance/list", status_code=302)

# ------- edit 

@router.get("/test/edit/{id}")
async def get_test_edit(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    """ 
    Редагування тесту.
    """
    test = db.get(Test, id)
    if not test:
        return RedirectResponse(url="/test/list", status_code=302)
    return templates.TemplateResponse("test/edit.html", {"request": request, "test": test})


@router.post("/test/edit/{id}")
async def post_test_edit(
    id: int,
    request: Request,
    title: str = Form(...),
    body: str = Form(...),
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    test = db.get(Test, id)
    if not test:
        return RedirectResponse(url="/test/list", status_code=302)
    if test.username != user.username:
        return RedirectResponse(url="/test/list", status_code=401)
  
    test.title = title
    test.body = body   
    db.commit()
    return RedirectResponse(url="/test/list", status_code=302)

# ------- del 

@router.get("/test/del/{id}")
async def get_test_del(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    """ 
    Видалення тесту.
    """
    test = db.get(Test, id)
    if not test:
        return RedirectResponse(url="/test/list", status_code=302)
    return templates.TemplateResponse("test/del.html", {"request": request, "test": test})


@router.post("/test/del/{id}")
async def post_test_del(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    test = db.get(Test, id)
    db.delete(test)
    db.commit()
    return RedirectResponse(url="/test/list", status_code=302)


