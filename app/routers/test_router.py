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