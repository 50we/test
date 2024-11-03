from fastapi import APIRouter, Request, UploadFile, File, Depends, Form, Cookie, HTTPException, status
from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import sys
import database
from pydantic import BaseModel
from routers import auth
router = APIRouter()

templates = Jinja2Templates(directory="tr1/")
sys.path.insert(1, '/Users/kas054/to_learn/wb/')


def get_image(photo_data):
    pass


class Feedback(BaseModel):
    feedback: str
    file: UploadFile


class Item(BaseModel):
    name: str


@router.get("/clients", response_class=HTMLResponse)
def clients(request: Request,
            conn: sqlite3.Connection = Depends(database.get_db),
            token: Annotated[str | None, Cookie()] = None):
    feedback = "SELECT feedback_id, photo_name , path, feedback, username from feedback;"
    photo_data = conn.execute(feedback).fetchall()
    # image_bytes = photo_data[0][-1]
    image_bytes = "test"
    # image_stream = io.BytesIO(image_bytes)
    return templates.TemplateResponse("clients.html", {"request": request, "photo_data": photo_data})


@router.post("/clients")
async def client(request: Request, feedback: str = Form(...),
                 file: UploadFile = File(...),
                 conn: sqlite3.Connection = Depends(database.get_db),
                 #  token: str = Depends(auth.oauth2_scheme),
                 url: Annotated[str | None, Form(...)] = None,
                 roles: Annotated[str | None, Cookie()] = None):
    try:
        token = request.headers.get("X-Authorization").split()[1]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "JWT"},
        )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "JWT"},
        )
    base_path = f"tr1/feedback_images/{file.filename}"
    contents = await file.read()
    sql = "INSERT INTO feedback (photo_name, path, feedback, username) VALUES (?, ?, ?, ?);"
    username = auth.get_user_from_token(token)
    val = [file.filename,
           f"feedback_images/{file.filename}", feedback, username]
    conn.execute(sql, val)
    conn.commit()
    with open(base_path, "wb+") as f:
        f.write(contents)
    return RedirectResponse("/clients", status_code=302)


@router.get("/clients/all")
async def info_all_users(request: Request,
                         conn: sqlite3.Connection = Depends(database.get_db)):
    sql = "SELECT * from users"
    result = conn.execute(sql).fetchall()
    return {"result": result}


@router.post("/clients/find_one")
def info_user(request: Request, item: Item,
              conn: sqlite3.Connection = Depends(database.get_db)):
    sql = "SELECT * from users where name=(?);"
    name_json = item.model_dump()
    name = name_json.get('name')
    result = conn.execute(sql, [name]).fetchone()
    # return JSONResponse(status_code=200, content=name_json)
    return {result}


@router.post("/clients/find")
def info_user(request: Request, item: Item,
              conn: sqlite3.Connection = Depends(database.get_db)):
    sql = "SELECT * from users where name=(?);"
    name_json = item.model_dump()
    name = name_json.get('name')
    result = conn.execute(sql, [name]).fetchone()
    # return JSONResponse(status_code=200, content=name_json)
    return templates.TemplateResponse("info_leaks_users.html", {"request": request, "info": result, "name": name})


@router.get("/clients/find", response_class=HTMLResponse)
def all_clients(request: Request):
    return templates.TemplateResponse("info_users_all.html", {"request": request})
