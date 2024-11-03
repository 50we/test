from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import database
from pydantic import BaseModel

templates = Jinja2Templates(directory="tr1/")
router = APIRouter()


class Comment(BaseModel):
    comment: str


def item_exists(id, conn):
    # check existance of product
    check = "SELECT EXISTS(SELECT 1 FROM chocolate WHERE name=(?));"
    return conn.execute(check, (id,)).fetchone()[0]


@router.get("/item/{item_id}/comments/", response_class=HTMLResponse)
def read_comments(request: Request, item_id: int,  conn: sqlite3.Connection = Depends(database.get_db)):
    query = "SELECT user_id, choco_id, comment from comments WHERE choco_id = (?);"
    comments = conn.execute(query, (item_id,)).fetchall()
    return templates.TemplateResponse("comments.html", {"request": request, "comments": comments, "item_id": item_id})


@router.get("/item", response_class=HTMLResponse)
def item_page(request: Request, id, conn: sqlite3.Connection = Depends(database.get_db)):  # remove id: int
    vuln_chocolate_info = conn.execute("""Select id, name, available, image from
                                        chocolate where id = \'{}\'""".format(id),
                                       ).fetchone()
    # chocolate_info = conn.execute("Select id, name, available, image from chocolate where id = (?)",
    #   (id,)).fetchone()
    name = vuln_chocolate_info[1]
    return templates.TemplateResponse("items.html", {"request": request, "info": vuln_chocolate_info, "name": name})


@router.post("/item/{item_id}/comments/")
def create_comment_for_product(request: Request, item_id: int, comment: Comment, 
                                conn: sqlite3.Connection = Depends(database.get_db)):
    # if not item_exists(item_id, conn):
    # redirect_url = "/item?id="+str(item_id)
    # return RedirectResponse(redirect_url, status_code=303)
    comment_json = comment.model_dump()
    text = comment_json.get('comment')
    user_id = 13
    query = "INSERT INTO comments (user_id, choco_id, comment) VALUES(?, ?, ?);"
    try:
        conn.execute(query, [user_id, item_id, text,])
    except Exception as e:
        return "an error occured: {}".format(e)
    conn.commit()
    redirect_url = "/item/{}/comments/".format(item_id)
    return RedirectResponse(redirect_url, status_code=303)
