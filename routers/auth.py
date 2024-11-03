from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from urllib.parse import quote_plus
from jose import JWTError, jwt
from base64 import b64encode
from fastapi import Request
from fastapi.templating import Jinja2Templates
from typing import Optional
from passlib.context import CryptContext
from pydantic import BaseModel
from hashlib import md5
import database
import sqlite3
import logging

templates = Jinja2Templates(directory="tr1/")

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str


class UserRequest(User):
    plain_password: str


pwd_context = CryptContext(schemes=["md5_crypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


def get_password(password) -> str:
    hash_func = md5()
    hash_func.update(bytes(password, "utf-8"))
    return hash_func.hexdigest()


def verify_password(plain_password, hashed_password):
    try:
        return get_password(plain_password) == hashed_password
    except ValueError:
        return False


def get_password_hash(password):
    return pwd_context.hash(password)


def user_info_dict(user_info: tuple) -> dict:
    columns = ['username', 'hashed_password']
    row_dict = {columns[i]: user_info[i] for i in range(len(columns))}
    return row_dict


def user_info(username: str, conn: sqlite3.Connection) -> dict:
    user_info = conn.execute(
        "SELECT name, password  FROM users WHERE name = (?)", [username,]).fetchone()
    return user_info_dict(user_info)


def check_user(user_login, conn):
    check = "SELECT EXISTS(SELECT 1 FROM users WHERE name=(?));"
    vuln_check = 'SELECT EXISTS(SELECT 1 FROM users WHERE name=\'{}\')'.format(
        user_login)
    # return conn.execute(check, (user_login,)).fetchone()[0]
    return conn.execute(vuln_check).fetchone()[0]


def get_user(conn, username: str) -> UserInDB:
    if check_user(username, conn):
        user_dict = user_info(username, conn)
        return UserInDB(**user_dict)


def authenticate_user(conn: sqlite3.Connection, username: str, password: str) -> UserInDB:
    user = get_user(conn, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.get("/auth/login", response_class=HTMLResponse)
def new_login(request: Request, message: Optional[str] = None):
    return templates.TemplateResponse("login1.html", {"request": request, "message": message})


def is_admin(username: str):
    return username == "admin"


def get_roles(username: str):
    role = b"admin" if is_admin(username) else b"user"
    return quote_plus(b64encode(role).decode())


@router.post("/auth/token")
def login_for_access_token(
    response: Response,
    request: Request,
    user_model: UserRequest,
    conn: sqlite3.Connection = Depends(database.get_db)
):
    logging.info(f"{request.url}")
    username = user_model.username
    password = user_model.plain_password
    user = authenticate_user(
        conn, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user": user.username}, expires_delta=access_token_expires
    )
    roles = get_roles(username)
    token_value = "Bearer {}".format(access_token)
    # response.set_cookie(key="Authorization",
    #                     value=token_value, samesite="None", path="/")
    response.set_cookie(key="roles", value=roles, samesite="None", path="/")
    request.session["username"] = username
    # redirect_url = "http://localhost:8000/users/" + username
    # return RedirectResponse(redirect_url, status_code=303)
    return {"access_token": access_token, "token_type": "Bearer"}


@router.get("/auth/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.get("/auth/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]


if __name__ == '__main__':
    conn = sqlite3.connect("database.db",  check_same_thread=False)
    user_request = UserRequest
    user_request.username = "admin"
    user_request.plain_password = "admin"
    print(user_request.plain_password)


def get_user_from_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload = jwt.decode(token, SECRET_KEY,
                             options={"verify_signature": False, "verify_exp": False})
        username: str = payload.get("user")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username
