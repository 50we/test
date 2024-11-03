from fastapi import FastAPI, Request, Form, Depends, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# from contrast.fastapi import ContrastMiddleware
from pydantic import BaseModel
import uvicorn
from database import create_db_and_tables, get_db
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
import os.path
from fastapi.security import OAuth2PasswordBearer
from jinja2 import Environment, FileSystemLoader
from routers import item, users, auth, admin, clients, files
import logging
import secrets
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from typing import Optional
from fastapi import status
import sqlite3

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w+",
                    format="%(asctime)s %(levelname)s %(message)s")

security = HTTPBasic()


class Item(BaseModel):
    name: str


def check_creds(
    # credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    # logging.info(f'{credentials=}')
    # current_username_bytes = credentials.username.encode("utf8")
    # correct_username_bytes = b"test"
    # is_correct_username = secrets.compare_digest(
    #     current_username_bytes, correct_username_bytes
    # )
    # current_password_bytes = credentials.password.encode("utf8")
    # correct_password_bytes = b"test"
    # is_correct_password = secrets.compare_digest(
    #     current_password_bytes, correct_password_bytes
    # )
    # if not (is_correct_username and is_correct_password):
    #     # return False
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect username or password",
    #         headers={"WWW-Authenticate": "Basic"},
    #     )
    return True


# app = FastAPI()
app = FastAPI(dependencies=[Depends(check_creds)])
# app.add_middleware(ContrastMiddleware, original_app=app)


app.add_middleware(SessionMiddleware, secret_key="??????", same_site='none')

app.include_router(item.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(clients.router)
app.include_router(files.router)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
env = Environment(
    loader=FileSystemLoader("/Users/kas054/to_lern/wb/tr1"),
    autoescape=False
)

origin = "http://[^\s]*"


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.on_event("shutdown")
def on_shutdown():
    pass
    # connection_close()


app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/fonts", StaticFiles(directory="tr1/fonts"), name="fonts")
app.mount("/js", StaticFiles(directory="tr1/js"), name="js")
app.mount("/images", StaticFiles(directory="tr1/images"), name="images")
app.mount("/feedback_images",
          StaticFiles(directory="tr1/feedback_images"), name="feedback_images")

templates = Jinja2Templates(directory="tr1/")


class User(BaseModel):
    username: str
    password: str


@app.get("/", response_class=HTMLResponse)
def about(request: Request):
    #     return request.url, request.method
    return templates.TemplateResponse("index.html", {"request": request, "id": id})


def make_list(choco_info):
    result = []
    for row in choco_info:
        row_dict = {"id": row[0], "name": row[1],
                    "available": row[2], "image": row[3]}
        result.append(row_dict)
    return result


@app.get("/image")
def get_image(filename: str):
    file = "tr1/" + filename
    if os.path.isfile(file):
        return FileResponse(file)
    else:
        return HTTPException(status_code=404, detail=f"File {file} not found")


@app.get("/chocolate", response_class=HTMLResponse)
def about(request: Request, conn: sqlite3.Connection = Depends(get_db)):
    chocolate_info = conn.execute(
        "Select id, name, available, image from chocolate").fetchall()
    logging.info(f"{request.url}")
    return templates.TemplateResponse("chocolate.html", {"request": request, "chocolate": chocolate_info})


@app.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
async def signup(user: str = Form(...), password: str = Form(...), conn: sqlite3.Connection = Depends(get_db)):
    # 1) check whether user with this login already exists
    default_money = 1000
    default_cookies = 1000
    if user == admin:
        role = "admin"
    else:
        role = "user"
    insert = "INSERT INTO users (name, password, role, money, cookies) VALUES(?, ?, ?, ?, ?);"
    if auth.check_user(user, conn):
        return RedirectResponse("/login?message=user+already+exists", status_code=303)
    else:
        password_hash = auth.get_password(password)
        conn.execute(insert, [user, password_hash, role,
                     default_money, default_cookies])
        conn.commit()
    return RedirectResponse("/auth/login?message=new+user+is+created", status_code=303)


# @app.post("/check_host")
# def check_host(request: Request, host=Form(...)):
#     os_command = True if system("ping -c 1 " + host) == 0 else False
#     answer = "Host is up" if os_command else "Host is down"
#     return answer


@app.get("/search", response_class=HTMLResponse)
def search(request: Request):
    logging.info(f"{request.url}")
    return templates.TemplateResponse("search1.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
def search(request: Request, item: Item, conn: sqlite3.Connection = Depends(get_db)):
    logging.info(f"{request.url}")
    name_json = item.model_dump()
    name = name_json.get('name')
    vuln_search = "select id, name, available, image from chocolate where name=\"{}\" ".format(
        name)
    chocolate_info = conn.execute(vuln_search).fetchone()
    return templates.TemplateResponse("items.html", {"request": request, "info": chocolate_info, "name": name})


@app.get("/change_passwd", response_class=HTMLResponse)
def change(request: Request):
    logging.info(f"{request.url}")
    return templates.TemplateResponse("change_passwd.html", {"request": request})


@app.post("/change_passwd")
def change(request: Request, message: Optional[str] = None,
           new_passwd: str = Form(...),
           conn: sqlite3.Connection = Depends(get_db)):
    logging.info(f"{request.url}")
    username = request.session["username"]
    password_hash = auth.get_password(new_passwd)
    update = "UPDATE users SET password=(?) WHERE name = (?) "
    conn.execute(update, [password_hash, username,])
    conn.commit()
    return RedirectResponse("/auth/login?", status_code=303)


if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, reload=True,
                host="127.0.0.1", workers=4)
    # conn = sqlite3.connect("database.db",  check_same_thread=False)
    # feedback = "SELECT * from feedback;"
    # photo_data = conn.execute(feedback)
    # # user_request = auth.UserRequest
    # # user_request.username = "admin"
    # # user_request.plain_password = "admin"
    # # print(user_request.plain_password)
    # conn.rollback()
    # conn.close()
    # Replace with the path to your images directory
    # directory_path = Path("/tr1/saved_images")
    # image_files = directory_path.glob('*.png')
    # for image in image_files:
    #     print(image)
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidXNlcjEyMzQiLCJleHAiOjE3MDU1OTIzMjN9.hEIU9yKOgjBDlcEzUXwu4TZh9iecpMTrH6k1p6iiIAw"
    user = auth.get_current_user(token)
    print(user)
    # comment = Comment
    # comment.comment = "text"
    # text = "test2"
    # query = "INSERT INTO comments (user_id, choco_id, comment) VALUES(?, ?, ?);"
    # conn.execute(query, [1, item_id, text,])
    # query = 'SELECT * from comments'
    # result = conn.execute(query).fetchall()
    # conn.commit()
    # conn.close()

# print(result)
