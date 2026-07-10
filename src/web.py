from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.api.scans import router as scans_router

#Abs path of the src directory
BASE_DIR = Path(__file__).resolve().parent

#FastAPI application
app = FastAPI(title="CVC Link Checker API", version="1.0.0")

templates = Jinja2Templates(directory=str(BASE_DIR/"templates"))

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

app.include_router(scans_router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the main Link checker dashboard
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )
