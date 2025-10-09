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

from app.models.models import Test
from app.routers.login_router import get_current_user
from ..dal import get_db  # Функція для отримання сесії БД
from ..models.pss_models import User
from ..models.models import Question
from ..models.parser import parse_test_body

import bcrypt



# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- list

@router.get("/test/list")
async def get_test_list(
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    """ 
    Усі тести поточного юзера (викладача).
    """
    # return the login page with error message
    
    if user.role != "tutor":
        return templates.TemplateResponse(
            "../login/login.html", 
            {"request": request, "error": user.role})
        
    all_tests = db.query(Test).all()

   
    tests = [t for t in all_tests if t.username == user.username ] 
    return templates.TemplateResponse("test/list.html", {"request": request, "tests": tests})

# ------- new 

@router.get("/test/new")
async def get_test_new(
    request: Request,
    user: User=Depends(get_current_user)
):
    """ 
    Створення нового теста поточного юзера (викладача). 
    """
    test = Test(title="", body="") 
    return templates.TemplateResponse("test/new.html", {"request": request, "test": test})


@router.post("/test/new")
async def post_test_new(
    request: Request,
    title: str = Form(...),
    body: str = Form(...),
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    
    questions: list[Question] = parse_test_body(body) #TODO verify
    test = Test(
        title = title,
        username = user.username, 
        body = body,
        questions = questions,
        seances = []
    )
    try:
        db.add(test) 
        db.commit()
    except Exception as e:
        db.rollback()
        err_mes = f"Error during a new test adding: {e}"
        return templates.TemplateResponse("test/new.html", {"request": request, "test": test})
    return RedirectResponse(url="/test/list", status_code=302)

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
        return RedirectResponse(url="/test/list", status_code=403)
 
    test.title = title

    if test.body != body:
        test.body = body  
        for q in test.questions:
            db.delete(q)
        test.questions = parse_test_body(body)

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
    if test.username != user.username:
        return RedirectResponse(url="/test/list", status_code=403)
    
    return templates.TemplateResponse("test/del.html", {"request": request, "test": test})


@router.post("/test/del/{id}")
async def post_test_del(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User=Depends(get_current_user)
):
    test = db.get(Test, id)
    # for q in test.questions:
    #     db.delete(q)
    # for s in test.seances:
    #     db.delete(s)

    db.delete(test)
    db.commit()
    return RedirectResponse(url="/test/list", status_code=302)
