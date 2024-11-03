from datetime import datetime, timedelta
from typing import Annotated
import urllib
import base64
from fastapi import Depends, APIRouter, HTTPException, status, Cookie
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="tr1/")

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def check_token(token: str) -> bool:
    pass

# check if roles==admin


def check_role(roles: str) -> bool:
    return base64.b64decode(urllib.parse.unquote(roles)).decode() != 'admin'


@router.get("/admin/secret", response_class=HTMLResponse)
def admin_secret(request: Request,
                 roles: Annotated[str | None, Cookie()] = None):

    try:
        token = request.headers.get("X-Authorization").split()[1]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "JWT"},
        )
    # check role == admin
    if not roles or check_role(roles):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Don't have enought permissions",
        )
    check_token(token)
    roles = urllib.parse.unquote(roles)
    decoded_bytes = base64.urlsafe_b64decode(roles)
    roles = decoded_bytes.decode('utf-8')
    return templates.TemplateResponse("secret_page.html", {"request": request, "roles": roles})
