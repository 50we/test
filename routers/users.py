from fastapi import APIRouter, Request, Cookie, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
import logging
from pydantic import BaseModel
router = APIRouter()

templates = Jinja2Templates(directory="tr1/")


@router.get("/users/admin", response_class=HTMLResponse)
def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@router.post("/users/{name}")
async def user(request: Request):
    logging.info(request.url)
    return "ok"


@router.get("/users/{name}")
def user(request: Request, name):
    return templates.TemplateResponse("users.html", {"request": request, "name": name})


@router.get("/users/{name}/send_money_form")
def send_money(request: Request, name):
    logging.info(f"{request.url}")
    return templates.TemplateResponse("send_money.html", {"request": request, "username": name})


@router.get("/users/{name}/send_money")
def send_money(request: Request, cvv: str,
               money: str, card: str):
    logging.info(f"{request.url}")
    return 200


class User(BaseModel):
    name: str


@router.post("/users/info/secrets")
def show_secrets(request: Request,
                 roles: Annotated[str | None, Cookie()] = None,
                 session: Annotated[str | None, Cookie()] = None):
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Don't have enought permissions",
        )
    return templates.TemplateResponse("users_secrets.html", {"request": request})
