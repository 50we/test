from pydantic import BaseModel
from fastapi import APIRouter, File, Depends
from fastapi.templating import Jinja2Templates
import httpx
from fastapi.responses import JSONResponse, FileResponse

templates = Jinja2Templates(directory="tr1/")
# router = APIRouter(dependencies=[Depends(check_creds)])
router = APIRouter()


class File(BaseModel):
    url: str


@router.post("/files/upload_from_url/")
async def upload_from_url(file: File):
    url = file.url
    # return url
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.status_code != 200:
        return JSONResponse(status_code=400, content={"detail": "Failed to download file"})
    file_name = url.split("/")[-1]
    file_content = response.text
    return {"file_name": file_name, "file_content": file_content}


@router.get("/files/document")
def get_image(filename: str):
    file = "tr1/" + filename
    return FileResponse(file)
