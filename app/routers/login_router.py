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
from ..dal import get_db_pss  # Функція для отримання сесії БД
from ..models.pss_models import User
import bcrypt

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- login

@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login/login.html", {"request": request})



# Вставляє JWT у HttpOnly cookie
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db_pss),
):
    user = get_authenticated_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Створення токену
    expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    claims = {"sub": user.username, "role": user.role, "exp": datetime.now() + expires_delta}
    access_token = jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)    
    
    if user.role == "tutor": 
        url = "/test/list"
    elif user.role == "student": 
        url = "/test/list"
    else:
         url = "/test/list"
    redirect = RedirectResponse(url, status_code=302)

    # Встановлюємо cookie у відповідь
    redirect.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,      # ❗ Забороняє доступ з JS
        # secure=True,        # ❗ Передавати лише по HTTPS
        samesite="lax",     # ❗ Захист від CSRF
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES, 
    )
    return redirect    
    
# --------------------------------

# Перевірка користувача
def get_authenticated_user(username: str, password: str, db: Session):
    user = db.get(User, username)
    ### на той випадок, якщо в базу вставляли юзера вручну
    if isinstance(user.hashed_password, str):
        user.hashed_password = user.hashed_password.encode('utf-8')
    ###    
    pass_is_ok = bcrypt.checkpw(password.encode('utf-8'), user.hashed_password)
    return user if pass_is_ok else None


# 🔑 описуємо джерело токена (cookie)
cookie_scheme = APIKeyCookie(name="access_token")

def get_current_user(token: str = Security(cookie_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return User(username=payload.get("sub"), role=payload.get("role"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")





#  ------------------------- 👤 Захищений маршрут
@router.get("/me")
async def read_me(user=Depends(get_current_user)):
    return user

